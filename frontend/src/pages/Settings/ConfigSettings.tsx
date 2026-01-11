import React, { useEffect, useState } from 'react';
import { Card, Button, Input, message, Spin, Space, Modal, Popconfirm, Empty, Select, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SoundOutlined, TeamOutlined } from '@ant-design/icons';
import { useConfigStore } from '../../stores/configStore';
import VoiceSelector from './VoiceSelector';
import type { VoiceGroup } from '../../types/config';
import './ConfigSettings.css';

const ConfigSettings: React.FC = () => {
  const { 
    roleList, isRoleListLoading, fetchRoleList, addRole, deleteRole, renameRole, updateRoleVoice, 
    voiceSettings, fetchVoiceSettings,
    groups, isGroupsLoading, fetchGroups, addGroup, updateGroup, deleteGroup,
    currentGroup, isCurrentGroupLoading, fetchCurrentGroup, setCurrentGroup
  } = useConfigStore();

  const [voiceSelectorVisible, setVoiceSelectorVisible] = useState(false);
  const [selectedRoleName, setSelectedRoleName] = useState<string | null>(null);
  const [addRoleModalVisible, setAddRoleModalVisible] = useState(false);
  const [renameModalVisible, setRenameModalVisible] = useState(false);
  const [newRoleName, setNewRoleName] = useState('');
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>('');
  const [renameRoleName, setRenameRoleName] = useState('');
  const [renameNewName, setRenameNewName] = useState('');
  
  const [groupManageModalVisible, setGroupManageModalVisible] = useState(false);
  const [addGroupModalVisible, setAddGroupModalVisible] = useState(false);
  const [editGroupModalVisible, setEditGroupModalVisible] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [editGroupName, setEditGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState<VoiceGroup | null>(null);

  useEffect(() => {
    fetchRoleList();
    fetchVoiceSettings();
    fetchGroups();
    fetchCurrentGroup();
  }, [fetchRoleList, fetchVoiceSettings, fetchGroups, fetchCurrentGroup]);

  const handleAddRole = async () => {
    if (!newRoleName.trim()) {
      message.error('请输入角色名称');
      return;
    }
    try {
      await addRole(newRoleName.trim());
      
      if (selectedVoiceId) {
        await updateRoleVoice(newRoleName.trim(), selectedVoiceId);
      }
      
      message.success('角色添加成功');
      setAddRoleModalVisible(false);
      setNewRoleName('');
      setSelectedVoiceId('');
    } catch (error) {
      message.error('角色添加失败，请重试');
    }
  };

  const handleDeleteRole = async (roleName: string) => {
    try {
      await deleteRole(roleName);
      message.success('角色删除成功');
    } catch (error) {
      message.error('角色删除失败，请重试');
    }
  };

  const handleRenameRole = async () => {
    if (!renameNewName.trim()) {
      message.error('请输入新角色名称');
      return;
    }
    try {
      await renameRole(renameRoleName, renameNewName.trim());
      message.success('角色重命名成功');
      setRenameModalVisible(false);
      setRenameRoleName('');
      setRenameNewName('');
    } catch (error) {
      message.error('角色重命名失败，请重试');
    }
  };

  const handleOpenVoiceSelector = (roleName: string) => {
    setSelectedRoleName(roleName);
    setVoiceSelectorVisible(true);
  };

  const handleSelectVoice = async (voiceId: string) => {
    if (selectedRoleName) {
      try {
        await updateRoleVoice(selectedRoleName, voiceId);
        message.success('音色设置成功');
      } catch (error) {
        message.error('音色设置失败，请重试');
      }
    }
  };

  const handleGroupChange = async (groupName: string) => {
    try {
      await setCurrentGroup(groupName);
      message.success('切换组别成功');
      await fetchRoleList();
    } catch (error) {
      message.error('切换组别失败，请重试');
    }
  };

  const handleAddGroup = async () => {
    if (!newGroupName.trim()) {
      message.error('请输入组别名称');
      return;
    }
    try {
      await addGroup({ name: newGroupName.trim(), role: {} });
      message.success('组别添加成功');
      setAddGroupModalVisible(false);
      setNewGroupName('');
      await fetchGroups();
    } catch (error) {
      message.error('组别添加失败，请重试');
    }
  };

  const handleEditGroup = async () => {
    if (!editGroupName.trim()) {
      message.error('请输入组别名称');
      return;
    }
    if (!selectedGroup) return;
    
    try {
      await updateGroup(selectedGroup.name, { name: editGroupName.trim() });
      message.success('组别修改成功');
      setEditGroupModalVisible(false);
      setEditGroupName('');
      setSelectedGroup(null);
      await fetchGroups();
    } catch (error) {
      message.error('组别修改失败，请重试');
    }
  };

  const handleDeleteGroup = async (groupName: string) => {
    try {
      await deleteGroup(groupName);
      message.success('组别删除成功');
      await fetchGroups();
      await fetchCurrentGroup();
    } catch (error) {
      message.error('组别删除失败，请重试');
    }
  };

  const getVoiceName = (voiceId: string) => {
    const voice = voiceSettings.find(v => v.voice_id === voiceId);
    return voice ? voice.name : voiceId;
  };

  return (
    <Card title="角色配置设置" className="role-settings-card">
      <Spin spinning={isRoleListLoading}>
        <div className="role-settings-content">
          <div className="role-settings-header">
            <Space size="middle">
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setAddRoleModalVisible(true)}
              >
                添加角色
              </Button>
              <Button
                icon={<TeamOutlined />}
                onClick={() => setGroupManageModalVisible(true)}
              >
                管理组别
              </Button>
            </Space>
          </div>

          <div className="group-selector">
            <span className="group-label">当前组别：</span>
            <Select
              value={currentGroup}
              onChange={handleGroupChange}
              loading={isCurrentGroupLoading}
              style={{ width: 200 }}
              options={groups.map(g => ({
                label: g.name,
                value: g.name
              }))}
            />
          </div>

          {roleList.length === 0 ? (
            <Empty description="暂无角色配置" />
          ) : (
            <div className="role-list">
              {roleList.map((role) => (
                <div key={role.name} className="role-item">
                  <div className="role-item-info">
                    <span className="role-item-name">{role.name}</span>
                    <span className="role-item-voice">
                      <SoundOutlined />
                      {role.voice_id ? getVoiceName(role.voice_id) : '未设置'}
                    </span>
                  </div>
                  <Space size="small">
                    <Button
                      type="text"
                      icon={<SoundOutlined />}
                      onClick={() => handleOpenVoiceSelector(role.name)}
                    >
                      设置音色
                    </Button>
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => {
                        setRenameRoleName(role.name);
                        setRenameNewName(role.name);
                        setRenameModalVisible(true);
                      }}
                    >
                      重命名
                    </Button>
                    <Popconfirm
                      title="确定要删除这个角色吗？"
                      onConfirm={() => handleDeleteRole(role.name)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  </Space>
                </div>
              ))}
            </div>
          )}
        </div>
      </Spin>

      <VoiceSelector
        visible={voiceSelectorVisible}
        onClose={() => {
          setVoiceSelectorVisible(false);
          setSelectedRoleName(null);
        }}
        onSelect={handleSelectVoice}
        currentVoiceId={selectedRoleName ? roleList.find(r => r.name === selectedRoleName)?.voice_id : undefined}
      />

      <Modal
        title="添加角色"
        open={addRoleModalVisible}
        onCancel={() => {
          setAddRoleModalVisible(false);
          setNewRoleName('');
          setSelectedVoiceId('');
        }}
        onOk={handleAddRole}
        okText="确定"
        cancelText="取消"
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <div style={{ marginBottom: 8 }}>角色名称</div>
            <Input
              placeholder="输入角色名称"
              value={newRoleName}
              onChange={(e) => setNewRoleName(e.target.value)}
              onPressEnter={handleAddRole}
              autoFocus
            />
          </div>
          <div>
            <div style={{ marginBottom: 8 }}>选择音色</div>
            <Select
              placeholder="请选择音色（可选）"
              style={{ width: '100%' }}
              value={selectedVoiceId || undefined}
              onChange={setSelectedVoiceId}
              allowClear
              options={voiceSettings.map(voice => ({
                label: `${voice.name} (${voice.gender})`,
                value: voice.voice_id
              }))}
            />
          </div>
        </Space>
      </Modal>

      <Modal
        title="重命名角色"
        open={renameModalVisible}
        onCancel={() => {
          setRenameModalVisible(false);
          setRenameRoleName('');
          setRenameNewName('');
        }}
        onOk={handleRenameRole}
        okText="确定"
        cancelText="取消"
      >
        <Input
          placeholder="输入新角色名称"
          value={renameNewName}
          onChange={(e) => setRenameNewName(e.target.value)}
          onPressEnter={handleRenameRole}
          autoFocus
        />
      </Modal>

      <Modal
        title="管理组别"
        open={groupManageModalVisible}
        onCancel={() => setGroupManageModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setGroupManageModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        <Spin spinning={isGroupsLoading}>
          <div className="group-management">
            <div className="group-management-header">
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setAddGroupModalVisible(true)}
              >
                添加组别
              </Button>
            </div>
            <div className="group-list">
              {groups.length === 0 ? (
                <Empty description="暂无组别" />
              ) : (
                groups.map((group) => (
                  <div key={group.name} className="group-item">
                    <div className="group-item-info">
                      <span className="group-item-name">
                        {group.name}
                        {group.name === currentGroup && (
                          <Tag color="blue" style={{ marginLeft: 8 }}>当前</Tag>
                        )}
                      </span>
                      <span className="group-item-count">
                        {Object.keys(group.role).length} 个角色
                      </span>
                    </div>
                    <Space size="small">
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => {
                          setSelectedGroup(group);
                          setEditGroupName(group.name);
                          setEditGroupModalVisible(true);
                        }}
                      >
                        编辑
                      </Button>
                      {group.name !== currentGroup && (
                        <Popconfirm
                          title="确定要删除这个组别吗？"
                          onConfirm={() => handleDeleteGroup(group.name)}
                          okText="确定"
                          cancelText="取消"
                        >
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                          >
                            删除
                          </Button>
                        </Popconfirm>
                      )}
                    </Space>
                  </div>
                ))
              )}
            </div>
          </div>
        </Spin>
      </Modal>

      <Modal
        title="添加组别"
        open={addGroupModalVisible}
        onCancel={() => {
          setAddGroupModalVisible(false);
          setNewGroupName('');
        }}
        onOk={handleAddGroup}
        okText="确定"
        cancelText="取消"
      >
        <div>
          <div style={{ marginBottom: 8 }}>组别名称</div>
          <Input
            placeholder="输入组别名称"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            onPressEnter={handleAddGroup}
            autoFocus
          />
        </div>
      </Modal>

      <Modal
        title="编辑组别"
        open={editGroupModalVisible}
        onCancel={() => {
          setEditGroupModalVisible(false);
          setEditGroupName('');
          setSelectedGroup(null);
        }}
        onOk={handleEditGroup}
        okText="确定"
        cancelText="取消"
      >
        <div>
          <div style={{ marginBottom: 8 }}>组别名称</div>
          <Input
            placeholder="输入组别名称"
            value={editGroupName}
            onChange={(e) => setEditGroupName(e.target.value)}
            onPressEnter={handleEditGroup}
            autoFocus
          />
        </div>
      </Modal>
    </Card>
  );
};

export default ConfigSettings;
