import React, { useEffect, useState, useRef } from 'react';
import { Card, Button, Empty, Progress, message, Dropdown } from 'antd';
import { FileTextOutlined, SoundOutlined, ExportOutlined, ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import { useProjectStore } from '../../stores';
import { useTaskStore } from '../../stores/taskStore';
import { batchGenerateScript } from '../../services/scriptService';
import { batchGenerateAudio } from '../../services/audioService';
import { downloadPpt } from '../../services/projectService';
import PageView from '../Project/PageView';
import type { PageViewRef } from '../Project/PageView';
import '../../styles/homePage.css';

const HomePage: React.FC = () => {
  const {
    currentProject,
    fetchProjects,
    clearErrors,
    convertPdf,
    setCurrentPage,
    currentPageNumber,
    refreshCurrentProject
  } = useProjectStore();
  
  const {
    startMonitoring,
    currentTaskProgress,
    clearCurrentTask
  } = useTaskStore();
  
  // 进度状态
  const [scriptProgress, setScriptProgress] = useState(0);
  const [audioProgress, setAudioProgress] = useState(0);
  const [scriptTaskId, setScriptTaskId] = useState<string | null>(null);
  const [audioTaskId, setAudioTaskId] = useState<string | null>(null);
  
  // 上传状态
  const [converting, setConverting] = useState(false);
  
  // 一键转换状态
  const [isConvertingAll, setIsConvertingAll] = useState(false);
  
  // 导出PPT状态
  const [exportingPpt, setExportingPpt] = useState(false);
  const [currentStep, setCurrentStep] = useState(0); // 0: 未开始, 1: 切分页面, 2: 生成口播稿, 3: 生成音频, 4: 完成
  const [overallProgress, setOverallProgress] = useState(0);
  
  // PageView组件引用
  const pageViewRef = useRef<PageViewRef>(null);

  // 初始化获取项目列表
  useEffect(() => {
    fetchProjects();
    return () => {
      clearErrors();
      clearCurrentTask();
    };
  }, [fetchProjects, clearErrors, clearCurrentTask]);
  
  // 监听任务进度
  useEffect(() => {
    if (currentTaskProgress) {
      if (currentTaskProgress.taskId === scriptTaskId) {
        setScriptProgress(currentTaskProgress.progress * 100);
        // 更新整体进度（切分页面占25%，口播稿占50%）
        if (isConvertingAll) {
          setOverallProgress(25 + (currentTaskProgress.progress * 50));
        }
        // 当脚本任务完成时，清理任务ID
        if (currentTaskProgress.progress >= 1.0) {
          setScriptTaskId(null);
          message.success('脚本生成完成');
          if (isConvertingAll) {
            // 脚本完成后自动开始音频生成
            setTimeout(() => {
              setCurrentStep(3);
              startAudioGeneration();
            }, 500); // 添加短暂延迟确保状态更新完成
          }
        }
        // 检查任务是否失败
        if (currentTaskProgress.status === 'failed') {
          const errorMessage = currentTaskProgress.errorMessage || '脚本生成失败';
          message.error(`脚本生成失败: ${errorMessage}`);
          
          // 如果是一键转换过程中出错，重置所有状态
          if (isConvertingAll) {
            setIsConvertingAll(false);
            setCurrentStep(0);
            setOverallProgress(0);
            setScriptProgress(0);
            setAudioProgress(0);
            setScriptTaskId(null);
            setAudioTaskId(null);
            
            // 清除当前任务监控
            clearCurrentTask();
          }
        }
      } else if (currentTaskProgress.taskId === audioTaskId) {
        setAudioProgress(currentTaskProgress.progress * 100);
        // 更新整体进度（切分页面25%，口播稿50%，音频25%）
        if (isConvertingAll) {
          setOverallProgress(75 + (currentTaskProgress.progress * 25));
        }
        // 当音频任务完成时，清理任务ID
        if (currentTaskProgress.progress >= 1.0) {
          setAudioTaskId(null);
          message.success('音频生成完成');
          if (isConvertingAll) {
            setCurrentStep(4); // 完成
            setIsConvertingAll(false);
            message.success('一键转换完成！');
          }
        }
        // 检查任务是否失败
        if (currentTaskProgress.status === 'failed') {
          const errorMessage = currentTaskProgress.errorMessage || '音频生成失败';
          message.error(`音频生成失败: ${errorMessage}`);
          
          // 如果是一键转换过程中出错，重置所有状态
          if (isConvertingAll) {
            setIsConvertingAll(false);
            setCurrentStep(0);
            setOverallProgress(0);
            setScriptProgress(0);
            setAudioProgress(0);
            setScriptTaskId(null);
            setAudioTaskId(null);
            
            // 清除当前任务监控
            clearCurrentTask();
          }
        }
      }
    }
  }, [currentTaskProgress, scriptTaskId, audioTaskId, isConvertingAll, clearCurrentTask]);
  
  // 组件挂载时恢复未完成的任务监控
  useEffect(() => {
    const restoreTaskMonitoring = async () => {
      // 恢复脚本任务监控
      if (scriptTaskId && scriptProgress < 100) {
        try {
          startMonitoring(scriptTaskId);
        } catch (error) {
          console.error('恢复脚本任务监控失败:', error);
          setScriptTaskId(null);
          setScriptProgress(0);
        }
      }
      
      // 恢复音频任务监控
      if (audioTaskId && audioProgress < 100) {
        try {
          startMonitoring(audioTaskId);
        } catch (error) {
          console.error('恢复音频任务监控失败:', error);
          setAudioTaskId(null);
          setAudioProgress(0);
        }
      }
    };
    
    restoreTaskMonitoring();
  }, []); // 只在组件挂载时执行一次

  const handleConvertPdf = async () => {
    if (!currentProject) {
      message.error('请先选择一个项目');
      return;
    }
    
    setConverting(true);
    try {
      await convertPdf(currentProject.id);
      message.success('PDF转换成功');
    } catch (error) {
      console.error('PDF转换失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`PDF转换失败: ${errorMessage}`);
    } finally {
      setConverting(false);
    }
  };

  // 一键转换函数
  const handleOneClickConvert = async () => {
    if (!currentProject) {
      message.error('请先选择一个项目');
      return;
    }
    
    setIsConvertingAll(true);
    setCurrentStep(1);
    setOverallProgress(0);
    setScriptProgress(0);
    setAudioProgress(0);
    
    try {
      // 第一步：切分页面
      message.info('开始切分页面...');
      setCurrentStep(1);
      setOverallProgress(10);
      await convertPdf(currentProject.id);
      setOverallProgress(25);
      message.success('页面切分完成');
      
      // 等待一小段时间确保项目状态完全更新
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 第二步：生成口播稿
      message.info('开始生成口播稿...');
      setCurrentStep(2);
      const scriptResponse = await batchGenerateScript({ project_id: currentProject.id });
      setScriptTaskId(scriptResponse.task_id);
      startMonitoring(scriptResponse.task_id);
      
      // 第三步：生成音频
      // 注意：这里不等待，音频生成会在脚本完成后自动触发
      
    } catch (error) {
      console.error('一键转换失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`一键转换失败: ${errorMessage}`);
      
      // 重置所有状态
      setIsConvertingAll(false);
      setCurrentStep(0);
      setOverallProgress(0);
      setScriptProgress(0);
      setAudioProgress(0);
      setScriptTaskId(null);
      setAudioTaskId(null);
      
      // 清除当前任务监控
      clearCurrentTask();
    }
  };

  const handleGenerateScript = async () => {
    if (!currentProject) {
      message.error('请先选择一个项目');
      return;
    }
    
    try {
      const response = await batchGenerateScript({ project_id: currentProject.id });
      setScriptTaskId(response.task_id);
      startMonitoring(response.task_id);
      message.success('脚本生成已开始');
    } catch (error) {
      console.error('生成脚本失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`生成脚本失败: ${errorMessage}`);
    }
  };

  const handleGenerateAudio = async () => {
    if (!currentProject) {
      message.error('请先选择一个项目');
      return;
    }
    
    try {
      const response = await batchGenerateAudio({ project_id: currentProject.id });
      setAudioTaskId(response.task_id);
      startMonitoring(response.task_id);
      message.success('音频生成已开始');
    } catch (error) {
      console.error('生成音频失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`生成音频失败: ${errorMessage}`);
    }
  };

  // 专门用于一键转换的音频生成函数（不显示消息）
  const startAudioGeneration = async () => {
    if (!currentProject) return;
    
    try {
      const response = await batchGenerateAudio({ project_id: currentProject.id });
      setAudioTaskId(response.task_id);
      startMonitoring(response.task_id);
      message.info('音频生成已开始');
    } catch (error) {
      console.error('生成音频失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`生成音频失败: ${errorMessage}`);
      
      // 如果是一键转换过程中出错，重置所有状态
      if (isConvertingAll) {
        setIsConvertingAll(false);
        setCurrentStep(0);
        setOverallProgress(0);
        setScriptProgress(0);
        setAudioProgress(0);
        setScriptTaskId(null);
        setAudioTaskId(null);
        
        // 清除当前任务监控
        clearCurrentTask();
      }
    }
  };

  const handleExportPpt = async () => {
    if (!currentProject) {
      message.error('请先选择一个项目');
      return;
    }
    
    setExportingPpt(true);
    try {
      const blob = await downloadPpt(currentProject.id);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // 使用项目名称作为文件名，替换扩展名为.pptx
      const fileName = currentProject.name.replace(/\.[^/.]+$/, '') + '.pptx';
      link.download = fileName;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('PPT导出成功');
    } catch (error) {
      console.error('导出PPT失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`导出PPT失败: ${errorMessage}`);
    } finally {
      setExportingPpt(false);
    }
  };

  const handleRefresh = async () => {
    try {
      // 执行刷新
      await refreshCurrentProject();
      message.success('项目已刷新');
      
      // 刷新PageView中的脚本和音频
      if (pageViewRef.current) {
        try {
          // 并行执行刷新操作
          await Promise.all([
            pageViewRef.current.refreshScript(),
            pageViewRef.current.refreshPageAudio(),
            pageViewRef.current.refreshAllDialogueAudio()
          ]);
        } catch (error) {
          console.error('刷新PageView数据失败:', error);
          const errorMessage = error instanceof Error ? error.message : '未知错误';
          message.error(`刷新PageView数据失败: ${errorMessage}`);
        }
      }
      
      // 刷新后继续监控未完成的任务（不需要重新开始，因为监控已经在进行中）
      if (scriptTaskId && scriptProgress < 100) {
        try {
          startMonitoring(scriptTaskId);
        } catch (error) {
          console.error('刷新后恢复脚本任务监控失败:', error);
          const errorMessage = error instanceof Error ? error.message : '未知错误';
          message.error(`恢复脚本任务监控失败: ${errorMessage}`);
        }
      }
      
      if (audioTaskId && audioProgress < 100) {
        try {
          startMonitoring(audioTaskId);
        } catch (error) {
          console.error('刷新后恢复音频任务监控失败:', error);
          const errorMessage = error instanceof Error ? error.message : '未知错误';
          message.error(`恢复音频任务监控失败: ${errorMessage}`);
        }
      }
    } catch (error) {
      console.error('刷新项目失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      message.error(`项目刷新失败: ${errorMessage}`);
    }
  };

  const handlePrevPage = () => {
    if (!currentProject || currentPageNumber <= 1) return;
    
    // 直接执行页面切换，不中断任何正在进行的任务
    setCurrentPage(currentPageNumber - 1);
  };

  const handleNextPage = () => {
    if (!currentProject || !currentProject.images || currentPageNumber >= currentProject.images.length) return;
    
    // 直接执行页面切换，不中断任何正在进行的任务
    setCurrentPage(currentPageNumber + 1);
  };

  // 上传组件配置
  // 不再需要上传配置，直接使用切分页面按钮

  return (
    <div className="home-page">
      {currentProject ? (
        <>
          <Card 
            className="project-operations"
            bodyStyle={{ boxShadow: 'none', borderRadius: 0 }}
            style={{ boxShadow: 'none', borderRadius: 0 }}
          >
            <div className="operation-buttons" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Button 
                  type="primary" 
                  onClick={handleOneClickConvert}
                  loading={isConvertingAll}
                  disabled={converting || scriptTaskId !== null || audioTaskId !== null}
                  style={{ fontSize: '16px', padding: '10px 32px', background: '#1890ff', border: 'none', borderRadius: '24px', boxShadow: '0 4px 12px rgba(24, 144, 255, 0.3)', fontWeight: 'bold' }}
                >
                  ✨ 一键生成 ✨
                </Button>
                
                <Button 
                  type="default" 
                  icon={<ExportOutlined />} 
                  onClick={handleExportPpt}
                  disabled={!currentProject.images || currentProject.images.length === 0 || isConvertingAll || converting || scriptTaskId !== null || audioTaskId !== null}
                  loading={exportingPpt}
                  style={{ fontSize: '16px', padding: '10px 32px', border: '2px solid #FF8C42', color: '#FF8C42', fontWeight: 'bold', borderRadius: '24px', background: '#FFFFFF' }}
                >
                  导出PPT
                </Button>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                {/* 高级工具下拉菜单 */}
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: '1',
                        label: (
                          <Button 
                            type="default" 
                            icon={<FileTextOutlined />} 
                            onClick={handleConvertPdf}
                            loading={converting}
                            disabled={isConvertingAll || scriptTaskId !== null || audioTaskId !== null}
                            block
                          >
                            切分页面
                          </Button>
                        ),
                      },
                      {
                        key: '2',
                        label: (
                          <Button 
                            type="default" 
                            icon={<FileTextOutlined />} 
                            onClick={handleGenerateScript}
                            disabled={!currentProject.images || currentProject.images.length === 0 || isConvertingAll || converting || scriptTaskId !== null || audioTaskId !== null}
                            loading={scriptTaskId !== null}
                            block
                          >
                            一键生成口播稿
                          </Button>
                        ),
                      },
                      {
                        key: '3',
                        label: (
                          <Button 
                            type="default" 
                            icon={<SoundOutlined />} 
                            onClick={handleGenerateAudio}
                            disabled={!currentProject.images || currentProject.images.length === 0 || isConvertingAll || converting || scriptTaskId !== null || audioTaskId !== null}
                            loading={audioTaskId !== null}
                            block
                          >
                            一键生成音频
                          </Button>
                        ),
                      },

                    ]
                  }}
                  trigger={['click']}
                >
                  <Button 
                    type="default" 
                    icon={<SettingOutlined />}
                    size="middle"
                    style={{ fontSize: '14px', padding: '8px 16px', borderRadius: '20px', border: '2px solid #FF8C42', color: '#FF8C42', fontWeight: '500', background: '#FFFFFF' }}
                  >
                    高级工具 ▼
                  </Button>
                </Dropdown>
                
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={handleRefresh}
                  disabled={isConvertingAll}
                  size="middle"
                  style={{ fontSize: '14px', padding: '8px 16px', borderRadius: '20px', border: '2px solid #52C41A', color: '#52C41A', fontWeight: '500', background: '#FFFFFF' }}
                >
                  刷新
                </Button>
              </div>
            </div>
            
            {/* 统一进度条 */}
            <div style={{ marginBottom: '16px' }}>
              <Progress 
                percent={isConvertingAll ? overallProgress : (scriptTaskId ? scriptProgress : audioProgress)} 
                status={isConvertingAll ? (currentStep === 4 ? 'success' : 'active') : 
                       (scriptTaskId ? (scriptProgress === 100 ? 'success' : 'active') : 
                       (audioTaskId ? (audioProgress === 100 ? 'success' : 'active') : 'normal'))}
                format={(percent) => `${percent?.toFixed(1)}%`}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
            </div>
          </Card>
          
          {/* 添加PageView组件 */}
          {currentProject.images && currentProject.images.length > 0 && (
            <PageView 
              ref={pageViewRef}
              projectId={currentProject.id} 
              pageNumber={currentPageNumber} 
              totalPages={currentProject.images.length}
              onPrevPage={handlePrevPage}
              onNextPage={handleNextPage}
            />
          )}
        </>
      ) : (
        <Card className="no-project-selected" bodyStyle={{ boxShadow: 'none', borderRadius: 0 }} style={{ boxShadow: 'none', borderRadius: 0 }}>
          <Empty
            description="请从左侧选择一个项目或创建新项目"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      )}
    </div>
  );
};

export default HomePage;
