import React from 'react';
import { Card, Tag, Button, Space } from 'antd';
import { CalendarOutlined } from '@ant-design/icons';
import type { Project } from '../../types';

interface ProjectCardProps {
  project: Project;
  onSelect?: (project: Project) => void;
  showActions?: boolean;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  onSelect, 
  showActions = true 
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const hasPdf = project.pdf_path && project.pdf_path.trim() !== '';
  const hasImages = project.images && project.images.length > 0;

  return (
    <Card
      hoverable
      className="project-card"
      actions={showActions ? [
        <Button type="link" onClick={() => onSelect?.(project)}>
          打开项目
        </Button>
      ] : undefined}
    >
      <Card.Meta
        title={
          <div className="project-card-title">
            {project.name}
          </div>
        }
        description={
          <div className="project-card-description">
            <Space size="small" direction="vertical" style={{ width: '100%' }}>
              <div className="project-status">
                {hasPdf ? (
                  <Tag color="green">已上传PDF</Tag>
                ) : (
                  <Tag color="orange">未上传PDF</Tag>
                )}
                
                {hasImages ? (
                  <Tag color="blue">{project.images.length} 页图片</Tag>
                ) : (
                  <Tag color="default">未转换图片</Tag>
                )}
              </div>
              
              <div className="project-meta">
                <div className="meta-item">
                  <CalendarOutlined />
                  <span>创建时间: {formatDate(project.created_at)}</span>
                </div>
                <div className="meta-item">
                  <CalendarOutlined />
                  <span>更新时间: {formatDate(project.updated_at)}</span>
                </div>
              </div>
            </Space>
          </div>
        }
      />
    </Card>
  );
};

export default ProjectCard;