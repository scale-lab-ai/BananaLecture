import React, { useState } from 'react';
import { Modal, Form, Input, Button, Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { useProjectStore } from '../../stores';
import type { UploadFile, RcFile } from 'antd/es/upload/interface';

const { Dragger } = Upload;

interface ProjectFormProps {
  visible: boolean;
  onClose: () => void;
}

const ProjectForm: React.FC<ProjectFormProps> = ({ visible, onClose }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const { createProject, uploadPdfAndConvert, fetchProject, isPdfConverting } = useProjectStore();

  const handleSubmit = async (values: { name: string }) => {
    if (fileList.length === 0) {
      message.error('请上传PDF文档');
      return;
    }

    setLoading(true);
    try {
      // 第一步：创建项目
      const newProject = await createProject(values.name);
      if (newProject) {
        // 第二步：上传PDF并自动切分
        await uploadPdfAndConvert(newProject.id, fileList[0].originFileObj as File);

        // 等待PDF转换完成
        if (isPdfConverting) {
          message.info('PDF转换中，请稍候...');
          // 转换完成后会自动刷新项目数据
          return;
        }

        message.success('项目创建成功，页面正在切分中...');

        // 第三步：重新获取项目数据以确保包含最新信息
        // fetchProject 会自动设置 currentProject
        await fetchProject(newProject.id);

        form.resetFields();
        setFileList([]);
        onClose();
      }
    } catch (error) {
      message.error('项目创建失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    setFileList([]);
    onClose();
  };

  const uploadProps = {
    name: 'pdf_file',
    multiple: false,
    accept: '.pdf',
    fileList,
    beforeUpload: (file: RcFile) => {
      if (file.type !== 'application/pdf') {
        message.error('只能上传PDF文件');
        return false;
      }
      if (file.size > 100 * 1024 * 1024) {
        message.error('文件大小不能超过100MB');
        return false;
      }
      // 创建符合UploadFile类型的对象，包含必要的uid属性
      const uploadFile: UploadFile = {
        uid: file.uid || `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`,
        name: file.name,
        status: 'done',
        originFileObj: file,
        size: file.size,
        type: file.type
      };
      setFileList([uploadFile]);
      return false; // 阻止自动上传
    },
    onRemove: () => {
      setFileList([]);
    }
  };

  return (
    <Modal
      title="创建新项目"
      open={visible}
      onCancel={handleCancel}
      footer={null}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        autoComplete="off"
      >
        <Form.Item
          label="项目名称"
          name="name"
          rules={[
            { required: true, message: '请输入项目名称' },
            { max: 50, message: '项目名称不能超过50个字符' },
            {
              pattern: /^[a-zA-Z0-9_-]+$/,
              message: '项目名称只能包含英文字母、数字、下划线和连字符'
            }
          ]}
        >
          <Input placeholder="请输入项目名称（仅支持英文字母、数字、_和-）" />
        </Form.Item>
        
        <Form.Item
          label="PDF文档"
          required
          tooltip="必须上传PDF文档才能创建项目"
        >
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              仅支持PDF格式，文件大小不超过100MB
            </p>
          </Dragger>
        </Form.Item>
        
        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
          <Button onClick={handleCancel} style={{ marginRight: 8 }}>
            取消
          </Button>
          <Button type="primary" htmlType="submit" loading={loading || isPdfConverting}>
            创建
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ProjectForm;