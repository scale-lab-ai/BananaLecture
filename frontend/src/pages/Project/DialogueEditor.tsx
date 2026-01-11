import React, { useState, useEffect } from 'react';
import { Form, Select, Input, Button, Space, message } from 'antd';
import type { DialogueItem } from '../../types/script';
import type { RoleItem } from '../../types/config';

const { TextArea } = Input;

interface DialogueEditorProps {
  dialogue: DialogueItem;
  roleList: RoleItem[];
  onSave: (values: Partial<DialogueItem>) => void;
  onCancel: () => void;
}

const DialogueEditor: React.FC<DialogueEditorProps> = ({ dialogue, roleList, onSave, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    form.setFieldsValue({
      role: dialogue.role,
      content: dialogue.content,
      emotion: dialogue.emotion,
      speed: dialogue.speed
    });
  }, [dialogue, form]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      await onSave(values);
    } catch (error) {
      console.error('保存对话失败:', error);
      message.error('保存对话失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
    >
      <Form.Item
        name="role"
        label="角色"
        rules={[{ required: true, message: '请选择角色' }]}
      >
        <Select>
          {roleList.map(role => (
            <Select.Option key={role.name} value={role.name}>
              {role.name}
            </Select.Option>
          ))}
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
      >
        <Select>
          <Select.Option value="慢">慢</Select.Option>
          <Select.Option value="正常">正常</Select.Option>
          <Select.Option value="快">快</Select.Option>
        </Select>
      </Form.Item>
      
      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            保存
          </Button>
          <Button onClick={onCancel}>
            取消
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default DialogueEditor;