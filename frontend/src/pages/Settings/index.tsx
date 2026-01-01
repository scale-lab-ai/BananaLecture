import React from 'react';
import { Tabs } from 'antd';
import EnvSettings from './EnvSettings';
import ConfigSettings from './ConfigSettings';

const Settings: React.FC = () => {
  const tabItems = [
    {
      key: 'env',
      label: '环境变量设置',
      children: <EnvSettings />,
    },
    {
      key: 'roles',
      label: '角色配置设置',
      children: <ConfigSettings />,
    },
  ];

  return (
    <div className="settings-page">
      <Tabs items={tabItems} defaultActiveKey="env" />
    </div>
  );
};

export default Settings;
