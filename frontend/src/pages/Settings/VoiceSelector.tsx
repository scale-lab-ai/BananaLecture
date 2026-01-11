import React, { useEffect, useState } from 'react';
import { Modal, Row, Col, Space, Select, Button, Form, Input, message, Spin, Popconfirm } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import type { VoiceSetting } from '../../types/config';
import { useConfigStore } from '../../stores/configStore';
import VoiceCard from './VoiceCard';
import './VoiceSelector.css';

interface VoiceSelectorProps {
  visible: boolean;
  onClose: () => void;
  onSelect: (voiceId: string) => void;
  currentVoiceId?: string;
}

const VoiceSelector: React.FC<VoiceSelectorProps> = ({ visible, onClose, onSelect, currentVoiceId }) => {
  const { voiceSettings, isVoiceLoading, fetchVoiceSettings, addVoiceSetting, deleteVoiceSetting } = useConfigStore();

  const [filters, setFilters] = useState({
    gender: undefined as string | undefined,
    age_group: undefined as string | undefined,
    language: undefined as string | undefined
  });

  const [addModalVisible, setAddModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      fetchVoiceSettings();
    }
  }, [visible, fetchVoiceSettings]);

  const handleFilterChange = (key: string, value: string | undefined) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const filteredVoices = voiceSettings.filter(voice => {
    if (filters.gender && voice.gender !== filters.gender) return false;
    if (filters.age_group && voice.age_group !== filters.age_group) return false;
    if (filters.language && voice.language !== filters.language) return false;
    return true;
  });

  const handleAddVoice = async (values: any) => {
    try {
      const newVoice: VoiceSetting = {
        voice_id: values.voice_id,
        name: values.name,
        gender: values.gender,
        age_group: values.age_group,
        language: values.language,
        description: values.description || '',
        example_url: values.example_url || ''
      };
      await addVoiceSetting(newVoice);
      message.success('音色添加成功');
      setAddModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('音色添加失败，请重试');
    }
  };

  const handleDeleteVoice = async (voiceId: string) => {
    try {
      await deleteVoiceSetting(voiceId);
      message.success('音色删除成功');
    } catch (error) {
      message.error('音色删除失败，请重试');
    }
  };

  const handleSelectVoice = (voiceId: string) => {
    onSelect(voiceId);
    onClose();
  };

  return (
    <Modal
      title="选择音色"
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1200}
      className="voice-selector-modal"
    >
      <Spin spinning={isVoiceLoading}>
        <div className="voice-selector">
          <div className="voice-selector-filters">
            <Space size="middle">
              <Select
                placeholder="性别"
                allowClear
                style={{ width: 120 }}
                value={filters.gender}
                onChange={(value) => handleFilterChange('gender', value)}
                options={[
                  { label: '男', value: '男' },
                  { label: '女', value: '女' }
                ]}
              />
              <Select
                placeholder="年龄"
                allowClear
                style={{ width: 120 }}
                value={filters.age_group}
                onChange={(value) => handleFilterChange('age_group', value)}
                options={[
                  { label: '少年', value: '少年' },
                  { label: '青年', value: '青年' },
                  { label: '中年', value: '中年' },
                  { label: '老年', value: '老年' }
                ]}
              />
              <Select
                placeholder="语言"
                allowClear
                style={{ width: 120 }}
                value={filters.language}
                onChange={(value) => handleFilterChange('language', value)}
                options={[
                  { label: '中文', value: '中文' },
                  { label: '英文', value: '英文' }
                ]}
              />
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setAddModalVisible(true)}
              >
                添加音色
              </Button>
            </Space>
          </div>

          <div className="voice-selector-grid">
            <Row gutter={[16, 16]}>
              {filteredVoices.map((voice) => (
                <Col xs={24} sm={12} md={8} lg={6} key={voice.voice_id}>
                  <div className="voice-card-wrapper">
                    <VoiceCard
                      voice={voice}
                      selected={voice.voice_id === currentVoiceId}
                      onSelect={handleSelectVoice}
                    />
                    <Popconfirm
                      title="确定要删除这个音色吗？"
                      onConfirm={() => handleDeleteVoice(voice.voice_id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        className="voice-card-delete-btn"
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  </div>
                </Col>
              ))}
            </Row>
          </div>
        </div>
      </Spin>

      <Modal
        title="添加音色"
        open={addModalVisible}
        onCancel={() => {
          setAddModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAddVoice}
        >
          <Form.Item
            name="voice_id"
            label="Voice ID"
            rules={[{ required: true, message: '请输入 Voice ID' }]}
          >
            <Input placeholder="输入 Voice ID" />
          </Form.Item>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入音色名称' }]}
          >
            <Input placeholder="输入音色名称" />
          </Form.Item>
          <Form.Item
            name="gender"
            label="性别"
            rules={[{ required: true, message: '请选择性别' }]}
          >
            <Select placeholder="选择性别">
              <Select.Option value="男">男</Select.Option>
              <Select.Option value="女">女</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="age_group"
            label="年龄组"
            rules={[{ required: true, message: '请选择年龄组' }]}
          >
            <Select placeholder="选择年龄组">
              <Select.Option value="少年">少年</Select.Option>
              <Select.Option value="青年">青年</Select.Option>
              <Select.Option value="中年">中年</Select.Option>
              <Select.Option value="老年">老年</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="language"
            label="语言"
            rules={[{ required: true, message: '请选择语言' }]}
          >
            <Select placeholder="选择语言">
              <Select.Option value="中文">中文</Select.Option>
              <Select.Option value="英文">英文</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea rows={3} placeholder="输入音色描述（可选）" />
          </Form.Item>
          <Form.Item
            name="example_url"
            label="试听 URL"
          >
            <Input placeholder="输入试听音频 URL（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </Modal>
  );
};

export default VoiceSelector;