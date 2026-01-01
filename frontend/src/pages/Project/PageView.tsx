import { useEffect, useState, useRef, useImperativeHandle, forwardRef } from 'react';
import { Card, Button, Space, Typography, message, Modal, Form, Select, Input, Spin } from 'antd';
import { PlayCircleOutlined, SoundOutlined, PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useProjectStore } from '../../stores';
import { useTaskStore } from '../../stores/taskStore';
import { generateScript, addDialogue, updateDialogue, deleteDialogue } from '../../services/scriptService';
import { generatePageAudio, getPageAudio, generateDialogueAudio, getDialogueAudio } from '../../services/audioService';
import type { DialogueItem, DialogueRole, EmotionType, SpeechSpeed } from '../../types/script';
import type { AudioPlayerState } from '../../types/audio';
import DialogueEditor from './DialogueEditor';
import '../../styles/PageView.css';

const { Text } = Typography;
const { TextArea } = Input;

interface PageViewProps {
  projectId: string;
  pageNumber: number;
  totalPages: number;
  onPrevPage: () => void;
  onNextPage: () => void;
}

// 暴露给父组件的方法接口
export interface PageViewRef {
  refreshScript: () => Promise<void>;
  refreshPageAudio: () => Promise<void>;
  refreshAllDialogueAudio: () => Promise<void>;
}

const PageView = forwardRef<PageViewRef, PageViewProps>(({ projectId, pageNumber, totalPages, onPrevPage, onNextPage }, ref) => {
  const {
    currentPageImage,
    currentPageScript,
    isImageLoading,
    isScriptLoading,
    imageError,
    getImage,
    getScript
  } = useProjectStore();
  
  const {
    startMonitoring,
    currentTaskProgress
  } = useTaskStore();
  
  // 本地状态
  const [script, setScript] = useState(currentPageScript);
  
  // 音频播放状态
  const [audioPlayerState, setAudioPlayerState] = useState<AudioPlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 1.0
  });
  
  // 页面音频任务ID
  const [pageAudioTaskId, setPageAudioTaskId] = useState<string | null>(null);
  const [pageAudioProgress, setPageAudioProgress] = useState(0);
  
  // 对话音频播放状态映射
  const [dialogueAudioStates, setDialogueAudioStates] = useState<Record<string, AudioPlayerState>>({});
  
  // 对话音频生成状态映射
  const [dialogueAudioGenerating, setDialogueAudioGenerating] = useState<Record<string, boolean>>({});
  
  // 编辑对话框状态
  const [editDialogueModalVisible, setEditDialogueModalVisible] = useState(false);
  const [editingDialogue, setEditingDialogue] = useState<DialogueItem | null>(null);
  
  // 添加对话表单状态
  const [addDialogueModalVisible, setAddDialogueModalVisible] = useState(false);
  const [addDialogueForm] = Form.useForm();
  
  // 音频元素引用
  const pageAudioRef = useRef<HTMLAudioElement | null>(null);
  const dialogueAudioRefs = useRef<Record<string, HTMLAudioElement | null>>({});
  
  // 暴露给父组件的方法
  useImperativeHandle(ref, () => ({
    refreshScript: async () => {
      try {
        await getScript(projectId, pageNumber);
        message.success('脚本已刷新');
      } catch (error) {
        console.error('刷新脚本失败:', error);
        message.error('刷新脚本失败');
      }
    },
    refreshPageAudio: async () => {
      try {
        if (pageAudioRef.current) {
          const response = await getPageAudio(projectId, pageNumber);
          const audioBlob = response.data;
          const audioUrl = URL.createObjectURL(audioBlob);
          
          if (pageAudioRef.current.src && pageAudioRef.current.src.startsWith('blob:')) {
            URL.revokeObjectURL(pageAudioRef.current.src);
          }
          
          pageAudioRef.current.src = audioUrl;
          console.log('页面音频已刷新:', audioUrl);
          message.success('页面音频已刷新');
        }
      } catch (error) {
        console.error('刷新页面音频失败:', error);
        message.error('刷新页面音频失败');
      }
    },
    refreshAllDialogueAudio: async () => {
      if (!script || !script.dialogues || script.dialogues.length === 0) {
        message.info('暂无对话音频可刷新');
        return;
      }
      
      let successCount = 0;
      let failCount = 0;
      
      for (const dialogue of script.dialogues) {
        try {
          let audio = dialogueAudioRefs.current[dialogue.id];
          
          if (!audio) {
            audio = new Audio();
            dialogueAudioRefs.current[dialogue.id] = audio;
          }
          
          const response = await getDialogueAudio(projectId, pageNumber, dialogue.id);
          const audioBlob = response.data;
          const audioUrl = URL.createObjectURL(audioBlob);
          
          if (audio.src && audio.src.startsWith('blob:')) {
            URL.revokeObjectURL(audio.src);
          }
          
          audio.src = audioUrl;
          successCount++;
        } catch (error) {
          console.error(`刷新对话音频失败 ${dialogue.id}:`, error);
          failCount++;
        }
      }
      
      if (successCount > 0) {
        message.success(`成功刷新 ${successCount} 个对话音频`);
      }
      if (failCount > 0) {
        message.error(`失败 ${failCount} 个对话音频`);
      }
    }
  }), [projectId, pageNumber, script, getScript]);
  
  // 获取图片和脚本数据
  useEffect(() => {
    if (projectId && pageNumber) {
      getImage(projectId, pageNumber);
      // 获取脚本数据
      getScript(projectId, pageNumber).catch(error => {
        console.error('获取脚本失败:', error);
      });
      
      // 页面切换时恢复音频任务监控（如果正在进行）
      const restorePageAudioMonitoring = async () => {
        if (pageAudioTaskId && pageAudioProgress < 100) {
          try {
            startMonitoring(pageAudioTaskId);
            console.log('页面切换后恢复音频任务监控:', pageAudioTaskId);
          } catch (error) {
            console.error('恢复页面音频任务监控失败:', error);
            setPageAudioTaskId(null);
            setPageAudioProgress(0);
          }
        }
      };
      
      restorePageAudioMonitoring();
    }
  }, [projectId, pageNumber, getImage]);
  
  // 同步脚本状态
  useEffect(() => {
    setScript(currentPageScript);
  }, [currentPageScript]);
  
  // 监听任务进度
  useEffect(() => {
    if (currentTaskProgress) {
      if (currentTaskProgress.taskId === pageAudioTaskId) {
        setPageAudioProgress(currentTaskProgress.progress * 100);
        
        // 如果任务完成，释放按钮状态
        if (currentTaskProgress.progress >= 1.0) {
          setPageAudioTaskId(null);
          setPageAudioProgress(0);
          message.success('页面音频生成完成');
        }
      }
    }
  }, [currentTaskProgress, pageAudioTaskId]);
  
  // 组件挂载时恢复未完成的任务监控
  useEffect(() => {
    const restoreTaskMonitoring = async () => {
      // 恢复页面音频任务监控
      if (pageAudioTaskId && pageAudioProgress < 100) {
        try {
          startMonitoring(pageAudioTaskId);
        } catch (error) {
          console.error('恢复页面音频任务监控失败:', error);
          setPageAudioTaskId(null);
          setPageAudioProgress(0);
        }
      }
    };
    
    restoreTaskMonitoring();
  }, []); // 只在组件挂载时执行一次
  
  // 生成页面脚本
  const handleGenerateScript = async () => {
    try {
      await generateScript({ project_id: projectId, page_number: pageNumber });
      message.success('脚本生成已开始');
      // 重新获取脚本
      setTimeout(() => {
        getScript(projectId, pageNumber).catch(error => {
          console.error('获取脚本失败:', error);
        });
      }, 1000);
    } catch (error) {
      console.error('生成脚本失败:', error);
      message.error('生成脚本失败');
    }
  };
  
  // 刷新页面音频
  const handleRefreshPageAudio = async () => {
    try {
      // 重新获取音频
      if (pageAudioRef.current) {
        const response = await getPageAudio(projectId, pageNumber);
        const audioBlob = response.data;
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // 如果之前有音频URL，先释放它
        if (pageAudioRef.current.src && pageAudioRef.current.src.startsWith('blob:')) {
          URL.revokeObjectURL(pageAudioRef.current.src);
        }
        
        pageAudioRef.current.src = audioUrl;
        console.log('页面音频已刷新:', audioUrl);
        message.success('页面音频已刷新');
      }
    } catch (error) {
      console.error('刷新页面音频失败:', error);
      message.error('刷新页面音频失败');
    }
  };

  // 生成页面音频
  const handleGeneratePageAudio = async () => {
    try {
      const response = await generatePageAudio({ project_id: projectId, page_number: pageNumber });
      setPageAudioTaskId(response.task_id);
      startMonitoring(response.task_id);
      message.success('音频生成已开始');
    } catch (error) {
      console.error('生成音频失败:', error);
      message.error('生成音频失败');
    }
  };
  
  // 播放页面音频
  const handlePlayPageAudio = async () => {
    if (pageAudioRef.current) {
      if (audioPlayerState.isPlaying) {
        pageAudioRef.current.pause();
        setAudioPlayerState(prev => ({ ...prev, isPlaying: false }));
      } else {
        // 每次播放都重新获取音频，不使用缓存
        try {
          const response = await getPageAudio(projectId, pageNumber);
          // 当responseType为'blob'时，返回的是整个响应对象，需要从response.data获取Blob
          const audioBlob = response.data;
          const audioUrl = URL.createObjectURL(audioBlob);
          
          // 如果之前有音频URL，先释放它
          if (pageAudioRef.current.src && pageAudioRef.current.src.startsWith('blob:')) {
            URL.revokeObjectURL(pageAudioRef.current.src);
          }
          
          pageAudioRef.current.src = audioUrl;
          console.log('页面音频URL已设置:', audioUrl);
          
          pageAudioRef.current.play();
          setAudioPlayerState(prev => ({ ...prev, isPlaying: true }));
        } catch (error) {
          console.error('获取音频失败:', error);
          message.error('获取音频失败');
          return;
        }
      }
    } else {
      // 创建音频元素
      const audio = new Audio();
      pageAudioRef.current = audio;
      
      try {
        const response = await getPageAudio(projectId, pageNumber);
        // 当responseType为'blob'时，返回的是整个响应对象，需要从response.data获取Blob
        const audioBlob = response.data;
        const audioUrl = URL.createObjectURL(audioBlob);
        audio.src = audioUrl;
        console.log('页面音频URL已设置:', audioUrl);
        
        audio.addEventListener('loadedmetadata', () => {
          setAudioPlayerState(prev => ({ 
            ...prev, 
            duration: audio.duration 
          }));
        });
        
        audio.addEventListener('timeupdate', () => {
          setAudioPlayerState(prev => ({ 
            ...prev, 
            currentTime: audio.currentTime 
          }));
        });
        
        audio.addEventListener('ended', () => {
          setAudioPlayerState(prev => ({ ...prev, isPlaying: false }));
        });
        
        audio.play();
        setAudioPlayerState(prev => ({ ...prev, isPlaying: true }));
      } catch (error) {
        console.error('获取音频失败:', error);
        message.error('获取音频失败');
      }
    }
  };
  
  // 生成对话音频
  const handleGenerateDialogueAudio = async (dialogueId: string) => {
    // 设置生成状态为true
    setDialogueAudioGenerating(prev => ({ ...prev, [dialogueId]: true }));
    
    try {
      const response = await generateDialogueAudio({ 
        project_id: projectId, 
        page_number: pageNumber, 
        dialogue_id: dialogueId 
      });
      
      // 更新对话内容（API返回的是更新后的dialogue对象）
      if (script) {
        setScript(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            dialogues: prev.dialogues.map(d => 
              d.id === dialogueId ? response.dialogue : d
            )
          };
        });
      }
      
      message.success('对话音频生成成功');
    } catch (error) {
      console.error('生成对话音频失败:', error);
      message.error('生成对话音频失败');
    } finally {
      // 无论成功或失败，都重置生成状态
      setDialogueAudioGenerating(prev => ({ ...prev, [dialogueId]: false }));
    }
  };
  
  // 刷新对话音频
  const handleRefreshDialogueAudio = async (dialogueId: string) => {
    try {
      // 重新获取音频
      let audio = dialogueAudioRefs.current[dialogueId];
      
      if (!audio) {
        // 如果音频元素不存在，创建一个新的
        audio = new Audio();
        dialogueAudioRefs.current[dialogueId] = audio;
      }
      
      const response = await getDialogueAudio(projectId, pageNumber, dialogueId);
      const audioBlob = response.data;
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // 如果之前有音频URL，先释放它
      if (audio.src && audio.src.startsWith('blob:')) {
        URL.revokeObjectURL(audio.src);
      }
      
      audio.src = audioUrl;
      console.log('对话音频已刷新:', dialogueId, audioUrl);
      message.success('对话音频已刷新');
      
      // 更新音频状态
      setDialogueAudioStates(prev => ({
        ...prev,
        [dialogueId]: {
          ...prev[dialogueId],
          duration: audio.duration || 0,
          currentTime: 0,
          isPlaying: false
        }
      }));
    } catch (error) {
      console.error('刷新对话音频失败:', error);
      message.error('刷新对话音频失败');
    }
  };

  // 播放对话音频
  const handlePlayDialogueAudio = async (dialogueId: string) => {
    const currentAudioState = dialogueAudioStates[dialogueId] || {
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      volume: 1.0
    };
    
    let audio = dialogueAudioRefs.current[dialogueId];
    
    if (audio) {
      if (currentAudioState.isPlaying) {
        audio.pause();
        setDialogueAudioStates(prev => ({
          ...prev,
          [dialogueId]: { ...prev[dialogueId], isPlaying: false }
        }));
      } else {
        audio.play();
        setDialogueAudioStates(prev => ({
          ...prev,
          [dialogueId]: { ...prev[dialogueId], isPlaying: true }
        }));
      }
    } else {
      // 创建音频元素
      audio = new Audio();
      dialogueAudioRefs.current[dialogueId] = audio;
      
      try {
        const response = await getDialogueAudio(projectId, pageNumber, dialogueId);
        // 当responseType为'blob'时，返回的是整个响应对象，需要从response.data获取Blob
        const audioBlob = response.data;
        const audioUrl = URL.createObjectURL(audioBlob);
        audio.src = audioUrl;
        console.log('对话音频URL已设置:', dialogueId, audioUrl);
        
        audio.addEventListener('loadedmetadata', () => {
          if (audio && dialogueAudioStates[dialogueId]) {
            setDialogueAudioStates(prev => ({
              ...prev,
              [dialogueId]: { ...prev[dialogueId], duration: audio!.duration }
            }));
          }
        });
        
        audio.addEventListener('timeupdate', () => {
          if (audio && dialogueAudioStates[dialogueId]) {
            setDialogueAudioStates(prev => ({
              ...prev,
              [dialogueId]: { ...prev[dialogueId], currentTime: audio!.currentTime }
            }));
          }
        });
        
        audio.addEventListener('ended', () => {
          setDialogueAudioStates(prev => ({
            ...prev,
            [dialogueId]: { ...prev[dialogueId], isPlaying: false }
          }));
        });
        
        audio.play();
        setDialogueAudioStates(prev => ({
          ...prev,
          [dialogueId]: { ...currentAudioState, isPlaying: true }
        }));
      } catch (error) {
        console.error('获取对话音频失败:', error);
        message.error('获取对话音频失败');
      }
    }
  };
  
  // 编辑对话
  const handleEditDialogue = (dialogue: DialogueItem) => {
    setEditingDialogue(dialogue);
    setEditDialogueModalVisible(true);
  };
  
  // 更新对话
  const handleUpdateDialogue = async (values: Partial<DialogueItem>) => {
    if (!editingDialogue) return;
    
    try {
      await updateDialogue(projectId, pageNumber, editingDialogue.id, {
        role: values.role as DialogueRole,
        content: values.content || '',
        emotion: values.emotion as EmotionType,
        speed: values.speed as SpeechSpeed
      });
      
      message.success('对话更新成功');
      setEditDialogueModalVisible(false);
      setEditingDialogue(null);
      
      // 重新获取脚本
      getScript(projectId, pageNumber).catch(error => {
        console.error('获取脚本失败:', error);
      });
    } catch (error) {
      console.error('更新对话失败:', error);
      message.error('更新对话失败');
    }
  };
  
  // 删除对话
  const handleDeleteDialogue = async (dialogueId: string) => {
    try {
      await deleteDialogue(projectId, pageNumber, dialogueId);
      message.success('对话删除成功');
      
      // 重新获取脚本
      getScript(projectId, pageNumber).catch(error => {
        console.error('获取脚本失败:', error);
      });
    } catch (error) {
      console.error('删除对话失败:', error);
      message.error('删除对话失败');
    }
  };
  
  // 添加对话
  const handleAddDialogue = async (values: {
    role: DialogueRole;
    content: string;
    emotion: EmotionType;
    speed: SpeechSpeed;
  }) => {
    try {
      await addDialogue(projectId, pageNumber, values);
      message.success('对话添加成功');
      setAddDialogueModalVisible(false);
      addDialogueForm.resetFields();
      
      // 重新获取脚本
      getScript(projectId, pageNumber).catch(error => {
        console.error('获取脚本失败:', error);
      });
    } catch (error) {
      console.error('添加对话失败:', error);
      message.error('添加对话失败');
    }
  };
  
  return (
    <div className="page-view">
      <div className="page-content" style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
        {/* 左侧图片展示区 */}
        <div className="image-section" style={{ flex: 1.6, display: 'flex', flexDirection: 'column' }}>
          <Card className="image-card" bodyStyle={{ padding: 0, flex: 1 }} style={{ borderRadius: 0, boxShadow: 'none', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div className="image-container" style={{ padding: '8px', backgroundColor: '#FFFFFF', textAlign: 'center', height: '400px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              {isImageLoading ? (
                <div className="image-loading" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%', height: '100%' }}>
                  <Spin size="large" />
                </div>
              ) : imageError ? (
                <div className="image-error" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%', height: '100%' }}>
                  <Text type="danger">图片加载失败: {imageError}</Text>
                </div>
              ) : currentPageImage ? (
                <img src={currentPageImage} alt={`页面 ${pageNumber}`} className="page-image" style={{ maxWidth: '100%', maxHeight: '100%', width: 'auto', height: 'auto', objectFit: 'contain', borderRadius: 0, boxShadow: 'none' }} />
              ) : (
                <div className="no-image" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%', height: '100%' }}>
                  <Text type="secondary">暂无图片</Text>
                </div>
              )}
            </div>
            
            {/* 页面级别操作按钮 - 移动到图片下方 */}
            <div className="page-operations" style={{ padding: '8px', backgroundColor: '#FFFFFF' }}>
              <Space wrap>
                <Button
                  type="primary"
                  icon={<EditOutlined />}
                  onClick={handleGenerateScript}
                  style={{ borderRadius: '20px', padding: '6px 16px', background: '#1890ff', border: 'none' }}
                >
                  生成口播稿
                </Button>
                <Button
                  icon={<SoundOutlined />}
                  onClick={handleGeneratePageAudio}
                  loading={!!pageAudioTaskId}
                  style={{ borderRadius: '20px', padding: '6px 16px' }}
                >
                  生成音频
                </Button>
                <Button
                  icon={<PlayCircleOutlined />}
                  onClick={handlePlayPageAudio}
                  style={{ borderRadius: '20px', padding: '6px 16px' }}
                >
                  {audioPlayerState.isPlaying ? '暂停音频' : '播放音频'}
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleRefreshPageAudio}
                  style={{ borderRadius: '20px', padding: '6px 16px' }}
                >
                  刷新音频
                </Button>

              </Space>
            </div>
          </Card>
        </div>
        
        {/* 右侧对话列表 */}
        <div className="dialogue-section" style={{ flex: 0.9 }}>
          <Card className="dialogue-card" bodyStyle={{ padding: '0', display: 'flex', flexDirection: 'column' }} style={{ borderRadius: 0, boxShadow: 'none', display: 'flex', flexDirection: 'column' }}>
            {isScriptLoading ? (
              <div className="dialogue-loading">
                <Spin size="large" />
              </div>
            ) : (currentPageScript && currentPageScript.dialogues.length > 0 ? (
              <div className="dialogue-list" style={{ height: '350px', overflowY: 'auto' }}>
                {currentPageScript.dialogues.map(dialogue => (
                  <div key={dialogue.id} className="dialogue-item">
                    <div className="dialogue-header">
                      <Text strong>{dialogue.role}</Text>
                      <Text type="secondary">[{dialogue.emotion}] [{dialogue.speed}]</Text>
                      <div className="dialogue-actions">
                        <Button
                          type="text"
                          size="small"
                          icon={<EditOutlined />}
                          onClick={() => handleEditDialogue(dialogue)}
                        />
                        <Button
                          type="text"
                          size="small"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => handleDeleteDialogue(dialogue.id)}
                        />
                      </div>
                    </div>
                    <div className="dialogue-content">
                      <Text>{dialogue.content}</Text>
                    </div>
                    <div className="dialogue-audio-controls">
                      <Button
                        type="primary"
                        size="small"
                        icon={<SoundOutlined />}
                        onClick={() => handleGenerateDialogueAudio(dialogue.id)}
                        loading={dialogueAudioGenerating[dialogue.id] || false}
                      >
                        生成音频
                      </Button>
                      <Button
                        type="default"
                        size="small"
                        icon={<PlayCircleOutlined />}
                        onClick={() => handlePlayDialogueAudio(dialogue.id)}
                      >
                        {dialogueAudioStates[dialogue.id]?.isPlaying ? '暂停音频' : '播放音频'}
                      </Button>
                      <Button
                        type="default"
                        size="small"
                        icon={<ReloadOutlined />}
                        onClick={() => handleRefreshDialogueAudio(dialogue.id)}
                      >
                        刷新音频
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-dialogue">
                <Text type="secondary">暂无对话内容</Text>
              </div>
            ))}
            
            {/* 添加对话按钮 */}
            <div className="add-dialogue-section" style={{ marginTop: '8px', padding: '8px' }}>
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={() => setAddDialogueModalVisible(true)}
                block
                style={{ borderRadius: '20px', padding: '8px', border: '1px dashed #1890ff', color: '#1890ff', fontWeight: '500', fontSize: '14px' }}
              >
                添加对话
              </Button>
            </div>
          </Card>
        </div>
      </div>
      
      {/* 编辑对话模态框 */}
      <Modal
        title="编辑对话"
        open={editDialogueModalVisible}
        onCancel={() => {
          setEditDialogueModalVisible(false);
          setEditingDialogue(null);
        }}
        footer={null}
      >
        {editingDialogue && (
          <DialogueEditor
            dialogue={editingDialogue}
            onSave={handleUpdateDialogue}
            onCancel={() => {
              setEditDialogueModalVisible(false);
              setEditingDialogue(null);
            }}
          />
        )}
      </Modal>
      
      {/* 添加对话模态框 */}
      <Modal
        title="添加对话"
        open={addDialogueModalVisible}
        onCancel={() => setAddDialogueModalVisible(false)}
        onOk={() => addDialogueForm.submit()}
      >
        <Form
          form={addDialogueForm}
          layout="vertical"
          onFinish={handleAddDialogue}
        >
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
            initialValue="旁白"
          >
            <Select>
              <Select.Option value="旁白">旁白</Select.Option>
              <Select.Option value="大雄">大雄</Select.Option>
              <Select.Option value="哆啦A梦">哆啦A梦</Select.Option>
              <Select.Option value="道具">道具</Select.Option>
              <Select.Option value="其他男声">其他男声</Select.Option>
              <Select.Option value="其他女声">其他女声</Select.Option>
              <Select.Option value="其他">其他</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入对话内容' }]}
          >
            <TextArea rows={4} placeholder="请输入对话内容" />
          </Form.Item>
          
          <Form.Item
            name="emotion"
            label="情感"
            rules={[{ required: true, message: '请选择情感' }]}
            initialValue="auto"
          >
            <Select>
              <Select.Option value="auto">auto</Select.Option>
              <Select.Option value="happy">happy</Select.Option>
              <Select.Option value="sad">sad</Select.Option>
              <Select.Option value="angry">angry</Select.Option>
              <Select.Option value="fearful">fearful</Select.Option>
              <Select.Option value="disgusted">disgusted</Select.Option>
              <Select.Option value="surprised">surprised</Select.Option>
              <Select.Option value="neutral">neutral</Select.Option>
              <Select.Option value="fluent">fluent</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="speed"
            label="语速"
            rules={[{ required: true, message: '请选择语速' }]}
            initialValue="正常"
          >
            <Select>
              <Select.Option value="慢">慢</Select.Option>
              <Select.Option value="正常">正常</Select.Option>
              <Select.Option value="快">快</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
      
      {/* 隐藏的音频元素 */}
      <audio ref={pageAudioRef} style={{ display: 'none' }} />
      
      {/* 页面导航 */}
      <div className="page-navigation" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '8px', padding: '8px', backgroundColor: '#FFFFFF', borderRadius: '8px', boxShadow: 'none' }}>
        <Button 
          onClick={onPrevPage}
          disabled={pageNumber <= 1}
          size="middle"
          style={{ marginRight: '8px' }}
        >
          ◀ 上一页
        </Button>
        <span className="page-info" style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
          {pageNumber} / {totalPages}
        </span>
        <Button 
          onClick={onNextPage}
          disabled={pageNumber >= totalPages}
          size="middle"
          style={{ marginLeft: '8px' }}
        >
          下一页 ▶
        </Button>
      </div>
    </div>
  );
});

PageView.displayName = 'PageView';

export default PageView;