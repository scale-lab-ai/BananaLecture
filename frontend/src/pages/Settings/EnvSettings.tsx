import React, { useEffect, useState } from 'react';
import { Card, Input, Button, message, Spin } from 'antd';
import { useConfigStore } from '../../stores/configStore';
import type { EnvConfig } from '../../types/config';

const { Password } = Input;

const EnvSettings: React.FC = () => {
  const { envConfig, isEnvLoading, envError, fetchEnvConfig, updateEnvConfig } = useConfigStore();
  const [formValues, setFormValues] = useState<EnvConfig>(envConfig);
  const [originalValues, setOriginalValues] = useState<EnvConfig>(envConfig);

  // 页面加载时获取配置
  useEffect(() => {
    fetchEnvConfig();
  }, [fetchEnvConfig]);

  // 当配置更新时，同步表单值
  useEffect(() => {
    setFormValues(envConfig);
    setOriginalValues(envConfig);
  }, [envConfig]);

  // 处理输入变化
  const handleChange = (key: keyof EnvConfig, value: string) => {
    setFormValues(prev => ({ ...prev, [key]: value }));
  };

  // 保存配置
  const handleSave = async () => {
    try {
      await updateEnvConfig(formValues);
      message.success('环境配置保存成功');
    } catch (error) {
      message.error(envError || '保存失败，请重试');
    }
  };

  // 重置表单
  const handleReset = () => {
    setFormValues(originalValues);
  };

  return (
    <Card title="环境变量设置" className="env-settings-card">
      <Spin spinning={isEnvLoading}>
        <div className="env-settings-form">
          {/* LLM OpenAI配置 */}
          <div className="form-item">
            <label htmlFor="LLM_OPENAI_API_KEY">LLM_OPENAI_API_KEY:</label>
            <Password
              id="LLM_OPENAI_API_KEY"
              value={formValues.LLM_OPENAI_API_KEY}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('LLM_OPENAI_API_KEY', e.target.value)}
              placeholder="输入OpenAI API Key"
              allowClear
              visibilityToggle
            />
          </div>

          <div className="form-item">
            <label htmlFor="LLM_OPENAI_BASE_URL">LLM_OPENAI_BASE_URL:</label>
            <Input
              id="LLM_OPENAI_BASE_URL"
              value={formValues.LLM_OPENAI_BASE_URL}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('LLM_OPENAI_BASE_URL', e.target.value)}
              placeholder="输入OpenAI API Base URL"
              allowClear
            />
          </div>

          <div className="form-item">
            <label htmlFor="LLM_OPENAI_MODEL">LLM_OPENAI_MODEL:</label>
            <Input
              id="LLM_OPENAI_MODEL"
              value={formValues.LLM_OPENAI_MODEL}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('LLM_OPENAI_MODEL', e.target.value)}
              placeholder="输入OpenAI模型名称"
              allowClear
            />
          </div>

          {/* Minimax Audio配置 */}
          <div className="form-item">
            <label htmlFor="MINIMAX_AUDIO_API_KEY">MINIMAX_AUDIO_API_KEY:</label>
            <Password
              id="MINIMAX_AUDIO_API_KEY"
              value={formValues.MINIMAX_AUDIO_API_KEY}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('MINIMAX_AUDIO_API_KEY', e.target.value)}
              placeholder="输入Minimax音频API Key"
              allowClear
              visibilityToggle
            />
          </div>

          <div className="form-item">
            <label htmlFor="MINIMAX_AUDIO_GROUP_ID">MINIMAX_AUDIO_GROUP_ID:</label>
            <Input
              id="MINIMAX_AUDIO_GROUP_ID"
              value={formValues.MINIMAX_AUDIO_GROUP_ID}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('MINIMAX_AUDIO_GROUP_ID', e.target.value)}
              placeholder="输入Minimax音频Group ID"
              allowClear
            />
          </div>

          <div className="form-item">
            <label htmlFor="MINIMAX_AUDIO_MODEL">MINIMAX_AUDIO_MODEL:</label>
            <Input
              id="MINIMAX_AUDIO_MODEL"
              value={formValues.MINIMAX_AUDIO_MODEL}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('MINIMAX_AUDIO_MODEL', e.target.value)}
              placeholder="输入Minimax音频模型名称"
              allowClear
            />
          </div>

          {/* 操作按钮 */}
          <div className="form-actions">
            <Button type="primary" onClick={handleSave} loading={isEnvLoading}>
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

export default EnvSettings;
