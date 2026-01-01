import React, { useState, useEffect } from 'react';
import { Layout, Menu, Spin } from 'antd';
import { SettingOutlined, HomeOutlined } from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ProjectList, ProjectForm } from '../project';
import { useProjectStore } from '../../stores';
import './Sidebar.css';

const { Sider } = Layout;

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [createProjectVisible, setCreateProjectVisible] = useState(false);
  
  const {
    projects,
    isLoading,
    currentProject,
    fetchProjects,
    setCurrentProject,
    refreshCurrentProject
  } = useProjectStore();

  const selectedKey = location.pathname;
  const isHomePage = selectedKey === '/';

  // 初始化获取项目列表
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // 处理项目选择
  const handleProjectSelect = async (projectId: string) => {
    const project = projects.find(p => p.id === projectId);
    if (project) {
      setCurrentProject(project);
      
      // 立即刷新项目数据
      try {
        await refreshCurrentProject();
      } catch (error) {
        console.error('刷新项目数据失败:', error);
      }
      
      // 如果不在主页，则导航到主页
      if (!isHomePage) {
        navigate('/');
      }
    }
  };

  // 处理创建项目
  const handleCreateProject = () => {
    setCreateProjectVisible(true);
  };

  // 关闭创建项目表单
  const handleCloseProjectForm = () => {
    setCreateProjectVisible(false);
  };

  return (
    <Sider width={260} className="sidebar" style={{ background: '#63C5F4', borderRadius: '0', margin: '0px', boxShadow: '2px 0 8px rgba(0, 0, 0, 0.1)' }}>
      <div className="sidebar-header" style={{ padding: '20px', textAlign: 'center', borderBottom: '2px solid #63C5F4', marginBottom: '16px', background: '#63C5F4' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#000', margin: 0 }}>🍌 Banana Lecture</h2>
      </div>
      
      <div className="sidebar-content">
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          style={{ borderRight: 0, background: 'transparent' }}
          items={[
            {
              key: '/',
              icon: <HomeOutlined style={{ fontSize: '18px', color: '#000000' }} />,
              label: <Link to="/" style={{ fontSize: '16px', fontWeight: '500', color: '#000000' }}>首页</Link>
            },
            {
              key: '/settings',
              icon: <SettingOutlined style={{ fontSize: '18px', color: '#000000' }} />,
              label: <Link to="/settings" style={{ fontSize: '16px', fontWeight: '500', color: '#000000' }}>设置</Link>
            }
          ]}
        />

        {isHomePage && (
          <div className="project-section" style={{ marginTop: '24px', padding: '16px', background: '#63C5F4' }} >
            <div className="section-title" style={{ fontSize: '18px', fontWeight: 'bold', color: '#000', marginBottom: '16px', textAlign: 'center' }}>项目管理</div>
            {isLoading ? (
              <div className="loading-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '16px' ,background: '#63C5F4'}}>
                <Spin size="small" />
                <span style={{ marginLeft: '8px', color: '#000' }}>加载项目列表...</span>
              </div>
            ) : (
              <ProjectList
                projects={projects}
                currentProjectId={currentProject?.id || null}
                onProjectSelect={handleProjectSelect}
                onProjectCreate={handleCreateProject}
              />
            )}
          </div>
        )}
      </div>

      <ProjectForm
        visible={createProjectVisible}
        onClose={handleCloseProjectForm}
      />
    </Sider>
  );
};

export default Sidebar;
