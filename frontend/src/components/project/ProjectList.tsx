import React from 'react';
import { Menu, Input, Modal, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { Project } from '../../types';
import { useProjectStore } from '../../stores';

const { confirm } = Modal;

interface ProjectListProps {
  projects: Project[];
  currentProjectId: string | null;
  onProjectSelect: (projectId: string) => void;
  onProjectCreate: () => void;
}

const ProjectList: React.FC<ProjectListProps> = ({
  projects,
  currentProjectId,
  onProjectSelect,
  onProjectCreate
}) => {
  const { updateProject, deleteProject } = useProjectStore();

  // 处理项目重命名
  const handleRenameProject = (projectId: string, currentName: string) => {
    let newName = currentName;
    
    Modal.confirm({
      title: '重命名项目',
      destroyOnHidden: true,
      content: (
        <Input
          defaultValue={currentName}
          placeholder="请输入项目名称"
          onChange={(e) => newName = e.target.value}
          autoFocus
        />
      ),
      onOk: async () => {
        if (!newName.trim()) {
          message.error('项目名称不能为空');
          return;
        }
        
        try {
          await updateProject(projectId, newName.trim());
          message.success('项目重命名成功');
        } catch (error) {
          message.error('项目重命名失败');
        }
      }
    });
  };

  // 处理项目删除
  const handleDeleteProject = (projectId: string, projectName: string) => {
    confirm({
      title: '确认删除',
      destroyOnHidden: true,
      content: `确定要删除项目"${projectName}"吗？此操作不可恢复。`,
      okText: '确定',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          await deleteProject(projectId);
          message.success('项目删除成功');
        } catch (error) {
          message.error('项目删除失败');
        }
      }
    });
  };

  // 创建项目菜单项
  const createProjectMenuItem = (project: Project) => {
    const isSelected = project.id === currentProjectId;
    
    return {
      key: project.id,
      icon: isSelected ? <div className="project-indicator active" /> : <div className="project-indicator" />,
      label: project.name,
      className: isSelected ? 'project-item selected' : 'project-item',
      onTitleClick: () => onProjectSelect(project.id),
      children: [
        {
          key: `${project.id}-rename`,
          icon: <EditOutlined />,
          label: '重命名',
          onClick: ({ domEvent }: { domEvent: React.MouseEvent }) => {
            domEvent.stopPropagation();
            handleRenameProject(project.id, project.name);
          }
        },
        {
          key: `${project.id}-delete`,
          icon: <DeleteOutlined />,
          label: '删除',
          onClick: ({ domEvent }: { domEvent: React.MouseEvent }) => {
            domEvent.stopPropagation();
            handleDeleteProject(project.id, project.name);
          }
        }
      ]
    };
  };

  // 创建菜单项数组
  const menuItems = [
    {
      key: 'create-project',
      icon: <PlusOutlined />,
      label: '新建项目',
      className: 'create-project-item',
      onClick: onProjectCreate
    },
    ...projects.map(createProjectMenuItem)
  ];

  return (
    <div className="project-list">
      <Menu
        mode="inline"
        selectedKeys={currentProjectId ? [currentProjectId] : []}
        style={{ borderRight: 0 }}
        items={menuItems}
      />
    </div>
  );
};

export default ProjectList;