import React, { useEffect, useState } from 'react';
import { Card, Input, Button, message, Spin } from 'antd';
import { useConfigStore } from '../../stores/configStore';
import type { RoleConfig } from '../../types/config';



const ConfigSettings: React.FC = () => {
  const { roleConfig, isRoleLoading, roleError, fetchRoleConfig, updateRoleConfig } = useConfigStore();
  const [formValues, setFormValues] = useState<RoleConfig>(roleConfig);
  const [originalValues, setOriginalValues] = useState<RoleConfig>(roleConfig);

  // 页面加载时获取配置
  useEffect(() => {
    fetchRoleConfig();
  }, [fetchRoleConfig]);

  // 当配置更新时，同步表单值
  useEffect(() => {
    setFormValues(roleConfig);
    setOriginalValues(roleConfig);
  }, [roleConfig]);

  // 处理输入变化
  const handleChange = (key: string, value: string) => {
    setFormValues(prev => ({ ...prev, [key]: value }));
  };

  // 保存配置
  const handleSave = async () => {
    try {
      await updateRoleConfig(formValues);
      message.success('角色配置保存成功');
    } catch (error) {
      message.error(roleError || '保存失败，请重试');
    }
  };

  // 重置表单
  const handleReset = () => {
    setFormValues(originalValues);
  };

  // 角色列表
  const roles = ['旁白', '大雄', '哆啦A梦', '其他男声', '其他女声', '其他'];

  return (
    <Card title="角色配置设置" className="role-settings-card">
      <Spin spinning={isRoleLoading}>
        <div className="role-settings-form">
          {roles.map((role) => (
            <div key={role} className="form-item">
              <label htmlFor={`role-${role}`}>{role}:</label>
              <Input
                id={`role-${role}`}
                value={formValues[role] || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(role, e.target.value)}
                placeholder={`输入${role}的音色配置`}
                allowClear
              />
            </div>
          ))}

          {/* 操作按钮 */}
          <div className="form-actions">
            <Button type="primary" onClick={handleSave} loading={isRoleLoading}>
              保存
            </Button>
            <Button onClick={handleReset} style={{ marginLeft: 16 }}>
              重置
            </Button>
          </div>
        </div>
      </Spin>
    </Card>
  );
};

export default ConfigSettings;
