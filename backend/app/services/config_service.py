import json
from typing import Dict, Any, Optional, List
import logging

from app.config import config_manager
from app.core.path_manager import path_manager

logger = logging.getLogger(__name__)


class ConfigService:
    """Configuration service class"""

    def __init__(self):
        """Initialize configuration service"""
        self.config_manager = config_manager

    def get_env_config(self) -> Dict[str, str]:
        """Get environment configuration"""
        try:
            config = self.config_manager.get_config()
            return {
                "LLM_OPENAI_API_KEY": config.env.LLM_OPENAI_API_KEY,
                "LLM_OPENAI_BASE_URL": config.env.LLM_OPENAI_BASE_URL,
                "LLM_OPENAI_MODEL": config.env.LLM_OPENAI_MODEL,
                "MINIMAX_AUDIO_API_KEY": config.env.MINIMAX_AUDIO_API_KEY,
                "MINIMAX_AUDIO_GROUP_ID": config.env.MINIMAX_AUDIO_GROUP_ID,
                "MINIMAX_AUDIO_MODEL": config.env.MINIMAX_AUDIO_MODEL
            }
        except Exception as e:
            logger.error(f"Failed to get environment configuration: {str(e)}")
            raise

    def update_env_config(self, env_updates: Dict[str, str]) -> None:
        """Update environment configuration"""
        try:
            # Update configuration
            self.config_manager.update_env_config(env_updates)

            # Save to .env file
            self.config_manager.save_env_config()

            logger.info("Environment configuration updated successfully")
        except Exception as e:
            logger.error(f"Failed to update environment configuration: {str(e)}")
            raise

    def get_role_config(self) -> Dict[str, str]:
        """Get role configuration"""
        try:
            config = self.config_manager.get_config()
            return config.roles.mapping
        except Exception as e:
            logger.error(f"Failed to get role configuration: {str(e)}")
            raise

    def get_default_role_config(self) -> Dict[str, str]:
        """Get default role configuration"""
        return {
            "旁白": "Chinese (Mandarin)_Male_Announcer",
            "大雄": "Chinese (Mandarin)_ExplorativeGirl",
            "哆啦A梦": "Chinese (Mandarin)_Pure-hearted_Boy",
            "其他男声": "Chinese (Mandarin)_Pure-hearted_Boy",
            "其他女声": "Chinese (Mandarin)_ExplorativeGirl",
            "其他": "Chinese (Mandarin)_Radio_Host"
        }

    def get_voice_settings(self) -> List[Dict[str, Any]]:
        """Get all voice settings from storage/config/audio_setting.json"""
        try:
            audio_setting_path = path_manager.get_storage_audio_setting_path()
            
            if audio_setting_path.exists():
                with open(audio_setting_path, 'r', encoding='utf-8') as f:
                    voice_settings = json.load(f)
                return voice_settings
            else:
                logger.warning(f"Audio setting file not found: {audio_setting_path}")
                return []
        except Exception as e:
            logger.error(f"Failed to get voice settings: {str(e)}")
            raise

    def add_voice_setting(self, voice_setting: Dict[str, Any]) -> None:
        """Add a new voice setting"""
        try:
            voice_settings = self.get_voice_settings()

            # Check if voice_id already exists
            voice_id = voice_setting.get('voice_id')
            if any(v['voice_id'] == voice_id for v in voice_settings):
                raise ValueError(f"Voice ID '{voice_id}' already exists")

            voice_settings.append(voice_setting)
            self._save_voice_settings(voice_settings)

            logger.info(f"Voice setting added successfully: {voice_id}")
        except Exception as e:
            logger.error(f"Failed to add voice setting: {str(e)}")
            raise

    def update_voice_setting(self, voice_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing voice setting"""
        try:
            voice_settings = self.get_voice_settings()

            # Find and update the voice setting
            found = False
            for voice in voice_settings:
                if voice['voice_id'] == voice_id:
                    voice.update(updates)
                    found = True
                    break

            if not found:
                raise ValueError(f"Voice ID '{voice_id}' not found")

            self._save_voice_settings(voice_settings)

            logger.info(f"Voice setting updated successfully: {voice_id}")
        except Exception as e:
            logger.error(f"Failed to update voice setting: {str(e)}")
            raise

    def delete_voice_setting(self, voice_id: str) -> None:
        """Delete a voice setting"""
        try:
            voice_settings = self.get_voice_settings()

            # Filter out the voice setting to delete
            original_length = len(voice_settings)
            voice_settings = [v for v in voice_settings if v['voice_id'] != voice_id]

            if len(voice_settings) == original_length:
                raise ValueError(f"Voice ID '{voice_id}' not found")

            self._save_voice_settings(voice_settings)

            logger.info(f"Voice setting deleted successfully: {voice_id}")
        except Exception as e:
            logger.error(f"Failed to delete voice setting: {str(e)}")
            raise

    def _save_voice_settings(self, voice_settings: List[Dict[str, Any]]) -> None:
        """Save voice settings to storage/config/audio_setting.json"""
        try:
            audio_setting_path = path_manager.get_storage_audio_setting_path()
            
            with open(audio_setting_path, 'w', encoding='utf-8') as f:
                json.dump(voice_settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save voice settings: {str(e)}")
            raise

    def get_role_list(self) -> List[Dict[str, str]]:
        """Get list of roles with their associated voice IDs from current group"""
        try:
            current_group = self.config_manager.get_current_group()
            groups = self.get_all_groups()
            
            # Find current group
            for group in groups:
                if group['name'] == current_group:
                    role_mapping = group.get('role', {})
                    return [{"name": role_name, "voice_id": voice_id} 
                            for role_name, voice_id in role_mapping.items()]
            
            # If group not found, return empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get role list: {str(e)}")
            raise

    def add_role(self, role_name: str, voice_id: str = "") -> None:
        """Add a new role to the current group"""
        try:
            current_group = self.config_manager.get_current_group()
            groups = self.get_all_groups()
            
            # Find current group
            group_found = False
            for group in groups:
                if group['name'] == current_group:
                    role_mapping = group.get('role', {})
                    
                    if role_name in role_mapping:
                        raise ValueError(f"Role '{role_name}' already exists in group '{current_group}'")
                    
                    role_mapping[role_name] = voice_id
                    group['role'] = role_mapping
                    group_found = True
                    break
            
            if not group_found:
                raise ValueError(f"Group '{current_group}' not found")
            
            # Save to audio_group.json
            storage_audio_group = path_manager.get_storage_audio_group_path()
            with open(storage_audio_group, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)

            logger.info(f"Role added successfully: {role_name} in group {current_group}")
        except Exception as e:
            logger.error(f"Failed to add role: {str(e)}")
            raise

    def delete_role(self, role_name: str) -> None:
        """Delete a role from the current group"""
        try:
            current_group = self.config_manager.get_current_group()
            groups = self.get_all_groups()
            
            # Find current group
            group_found = False
            for group in groups:
                if group['name'] == current_group:
                    role_mapping = group.get('role', {})
                    
                    if role_name not in role_mapping:
                        raise ValueError(f"Role '{role_name}' not found in group '{current_group}'")
                    
                    del role_mapping[role_name]
                    group['role'] = role_mapping
                    group_found = True
                    break
            
            if not group_found:
                raise ValueError(f"Group '{current_group}' not found")
            
            # Save to audio_group.json
            storage_audio_group = path_manager.get_storage_audio_group_path()
            with open(storage_audio_group, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)

            logger.info(f"Role deleted successfully: {role_name} from group {current_group}")
        except Exception as e:
            logger.error(f"Failed to delete role: {str(e)}")
            raise

    def rename_role(self, old_name: str, new_name: str) -> None:
        """Rename a role in the current group"""
        try:
            current_group = self.config_manager.get_current_group()
            groups = self.get_all_groups()
            
            # Find current group
            group_found = False
            for group in groups:
                if group['name'] == current_group:
                    role_mapping = group.get('role', {})
                    
                    if old_name not in role_mapping:
                        raise ValueError(f"Role '{old_name}' not found in group '{current_group}'")
                    
                    if new_name in role_mapping:
                        raise ValueError(f"Role '{new_name}' already exists in group '{current_group}'")
                    
                    # Rename the role
                    voice_id = role_mapping[old_name]
                    del role_mapping[old_name]
                    role_mapping[new_name] = voice_id
                    
                    group['role'] = role_mapping
                    group_found = True
                    break
            
            if not group_found:
                raise ValueError(f"Group '{current_group}' not found")
            
            # Save to audio_group.json
            storage_audio_group = path_manager.get_storage_audio_group_path()
            with open(storage_audio_group, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)

            logger.info(f"Role renamed successfully: {old_name} -> {new_name} in group {current_group}")
        except Exception as e:
            logger.error(f"Failed to rename role: {str(e)}")
            raise

    def update_role_voice(self, role_name: str, voice_id: str) -> None:
        """Update the voice ID for a role in the current group"""
        try:
            current_group = self.config_manager.get_current_group()
            groups = self.get_all_groups()
            
            # Find current group
            group_found = False
            for group in groups:
                if group['name'] == current_group:
                    role_mapping = group.get('role', {})
                    
                    if role_name not in role_mapping:
                        raise ValueError(f"Role '{role_name}' not found in group '{current_group}'")
                    
                    role_mapping[role_name] = voice_id
                    group['role'] = role_mapping
                    group_found = True
                    break
            
            if not group_found:
                raise ValueError(f"Group '{current_group}' not found")
            
            # Save to audio_group.json
            storage_audio_group = path_manager.get_storage_audio_group_path()
            with open(storage_audio_group, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)

            logger.info(f"Role voice updated successfully: {role_name} -> {voice_id} in group {current_group}")
        except Exception as e:
            logger.error(f"Failed to update role voice: {str(e)}")
            raise

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """Get all voice groups"""
        try:
            storage_audio_group = path_manager.get_storage_audio_group_path()
            
            if storage_audio_group.exists():
                with open(storage_audio_group, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return []
        except Exception as e:
            logger.error(f"Failed to get all groups: {str(e)}")
            raise

    def add_group(self, group_name: str, role_mapping: Dict[str, str]) -> None:
        """Add a new voice group"""
        try:
            groups = self.get_all_groups()
            
            if any(g['name'] == group_name for g in groups):
                raise ValueError(f"Group '{group_name}' already exists")
            
            groups.append({
                "name": group_name,
                "role": role_mapping
            })
            
            storage_audio_group = path_manager.get_storage_audio_group_path()
            with open(storage_audio_group, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)

            logger.info(f"Group added successfully: {group_name}")
        except Exception as e:
            logger.error(f"Failed to add group: {str(e)}")
            raise

    def update_group(self, group_name: str, new_name: Optional[str] = None, role_mapping: Optional[Dict[str, str]] = None) -> None:
        """Update a voice group"""
        try:
            groups = self.get_all_groups()
            
            found = False
            for group in groups:
                if group['name'] == group_name:
                    if new_name is not None:
                        group['name'] = new_name
                    if role_mapping is not None:
                        group['role'] = role_mapping
                    found = True
                    break
            
            if not found:
                raise ValueError(f"Group '{group_name}' not found")
            
            storage_audio_group = path_manager.get_storage_audio_group_path()
            with open(storage_audio_group, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)

            logger.info(f"Group updated successfully: {group_name}")
        except Exception as e:
            logger.error(f"Failed to update group: {str(e)}")
            raise

    def delete_group(self, group_name: str) -> None:
        """Delete a voice group"""
        try:
            groups = self.get_all_groups()
            
            if not any(g['name'] == group_name for g in groups):
                raise ValueError(f"Group '{group_name}' not found")
            
            groups = [g for g in groups if g['name'] != group_name]
            
            storage_audio_group = path_manager.get_storage_audio_group_path()
            with open(storage_audio_group, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)

            logger.info(f"Group deleted successfully: {group_name}")
        except Exception as e:
            logger.error(f"Failed to delete group: {str(e)}")
            raise

    def get_current_group(self) -> str:
        """Get current selected group"""
        try:
            storage_config_json = path_manager.get_storage_config_json_path()
            
            if storage_config_json.exists():
                with open(storage_config_json, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get('current_group', 'default')
            
            return 'default'
        except Exception as e:
            logger.error(f"Failed to get current group: {str(e)}")
            raise

    def set_current_group(self, group_name: str) -> None:
        """Set current selected group"""
        try:
            storage_config_json = path_manager.get_storage_config_json_path()
            
            config_data = {}
            if storage_config_json.exists():
                with open(storage_config_json, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            config_data['current_group'] = group_name
            
            with open(storage_config_json, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Current group set successfully: {group_name}")
        except Exception as e:
            logger.error(f"Failed to set current group: {str(e)}")
            raise
