import React from 'react';
import { Card, Tag, Button, Space } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import type { VoiceSetting } from '../../types/config';
import './VoiceCard.css';

interface VoiceCardProps {
  voice: VoiceSetting;
  onSelect?: (voiceId: string) => void;
  selected?: boolean;
}

const VoiceCard: React.FC<VoiceCardProps> = ({ voice, onSelect, selected }) => {
  const handlePlay = () => {
    if (voice.example_url) {
      const audio = new Audio(voice.example_url);
      audio.play();
    }
  };

  const handleSelect = () => {
    if (onSelect) {
      onSelect(voice.voice_id);
    }
  };

  const getGenderColor = (gender: string) => {
    return gender === '男' ? 'blue' : 'pink';
  };

  const getAgeColor = (ageGroup: string) => {
    const colorMap: Record<string, string> = {
      '少年': 'green',
      '青年': 'orange',
      '中年': 'purple',
      '老年': 'gray'
    };
    return colorMap[ageGroup] || 'default';
  };

  const getLanguageColor = (language: string) => {
    return language === '中文' ? 'cyan' : 'geekblue';
  };

  return (
    <Card
      hoverable
      className={`voice-card ${selected ? 'voice-card-selected' : ''}`}
      onClick={handleSelect}
      style={{
        borderColor: selected ? '#1890ff' : undefined,
        boxShadow: selected ? '0 0 0 2px rgba(24, 144, 255, 0.2)' : undefined
      }}
    >
      <div className="voice-card-content">
        <div className="voice-card-header">
          <h3 className="voice-card-name">{voice.name}</h3>
          <Space size={4}>
            <Tag color={getGenderColor(voice.gender)}>{voice.gender}</Tag>
            <Tag color={getAgeColor(voice.age_group)}>{voice.age_group}</Tag>
            <Tag color={getLanguageColor(voice.language)}>{voice.language}</Tag>
          </Space>
        </div>

        <p className="voice-card-description">{voice.description}</p>

        <div className="voice-card-footer">
          {voice.example_url && (
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                handlePlay();
              }}
            >
              试听
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default VoiceCard;