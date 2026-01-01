import React from 'react';
import { Layout } from 'antd';
import Sidebar from './Sidebar';

const { Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh', background: '#ffffffff' }}>
      <Sidebar />
      <Layout>
        <Content style={{ margin: '0', overflow: 'auto' }}>
          <div style={{ 
            padding: 16, 
            minHeight: 'calc(100vh)',
            background: '#FFFFFF',
            borderRadius: '0'
          }}>
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};
export default MainLayout;
