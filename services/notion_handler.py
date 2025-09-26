import logging
from notion_client import Client
from config.config import Config

logger = logging.getLogger(__name__)

class NotionHandler:
    """Handles Notion API operations."""
    
    def __init__(self):
        self.client = Client(auth=Config.get_notion_token())
        self.database_id = Config.get_notion_database_id()
    
    def get_database_properties(self):
        """Get the properties of the Notion database."""
        try:
            response = self.client.databases.retrieve(database_id=self.database_id)
            return response['properties']
        except Exception as e:
            logger.error(f"Error retrieving database properties: {e}")
            return None
    
    def create_content_page(self, idea_data: dict, category: str):
        """Create a new page in Notion database for the generated idea."""
        if not self.database_id:
            logger.warning("Notion database ID not configured, skipping Notion save.")
            return
        
        guion_blocks = self._create_styled_guion_blocks(idea_data)
        
        properties = {
            "Nombre - idea": {
                "title": [
                    {
                        "text": {
                            "content": idea_data.get('es', {}).get('title', 'Sin título')
                        }
                    }
                ]
            },
            "Estado": {
                "status": {
                    "name": "Guion"
                }
            },
            "Área": {
                "multi_select": [
                    {"name": category}
                ]
            },
            "Falta contenido visual": {
                "checkbox": True
            }
        }
        
        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                icon={
                    "type": "emoji",
                    "emoji": "💡"
                },
                properties=properties,
                children=guion_blocks
            )
            logger.info(f"Created Notion page: {response['id']}")
        except Exception as e:
            logger.error(f"Error creating Notion page: {e}")
    
    def _create_styled_guion_blocks(self, idea_data: dict) -> list:
        """Create styled Notion blocks for the guion content."""
        blocks = []
        
        # Title
        blocks.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📝 Guion de Contenido"
                        }
                    }
                ]
            }
        })
        if 'es' in idea_data:
            es = idea_data['es']
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🇪🇸 Versión en Español"
                            }
                        }
                    ]
                }
            })
            
            # Title
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"🎯 Título: {es.get('title', '')}"
                            },
                            "annotations": {
                                "bold": True
                            }
                        }
                    ]
                }
            })
            
            # Script sections
            if 'script' in es:
                script = es['script']
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎬 Guion"
                                }
                            }
                        ]
                    }
                })
                
                # Hook
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🪝 Gancho: "
                                },
                                "annotations": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": {
                                    "content": script.get('gancho', '')
                                }
                            }
                        ]
                    }
                })
                
                # Body
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "📖 Cuerpo: "
                                },
                                "annotations": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": {
                                    "content": script.get('cuerpo', '')
                                }
                            }
                        ]
                    }
                })
                
                # Closing
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎯 Cierre: "
                                },
                                "annotations": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": {
                                    "content": script.get('cierre', '')
                                }
                            }
                        ]
                    }
                })
            
            # Hashtags
            if es.get('hashtags'):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🏷️ Hashtags"
                                }
                            }
                        ]
                    }
                })
                
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": es['hashtags']
                                },
                                "annotations": {
                                    "code": True
                                }
                            }
                        ]
                    }
                })
            
            # Video prompts
            if 'video_prompts' in es and es['video_prompts']:
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎥 Prompts de Video"
                                }
                            }
                        ]
                    }
                })
                
                for i, prompt in enumerate(es['video_prompts'], 1):
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Video {i}: {prompt}"
                                    }
                                }
                            ]
                        }
                    })
        
        # English version
        if 'en' in idea_data:
            en = idea_data['en']
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🇺🇸 English Version"
                            }
                        }
                    ]
                }
            })
            
            # Title
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"🎯 Title: {en.get('title', '')}"
                            },
                            "annotations": {
                                "bold": True
                            }
                        }
                    ]
                }
            })
            
            # Script sections
            if 'script' in en:
                script = en['script']
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎬 Script"
                                }
                            }
                        ]
                    }
                })
                
                # Hook
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🪝 Hook: "
                                },
                                "annotations": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": {
                                    "content": script.get('gancho', '')
                                }
                            }
                        ]
                    }
                })
                
                # Body
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "📖 Body: "
                                },
                                "annotations": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": {
                                    "content": script.get('cuerpo', '')
                                }
                            }
                        ]
                    }
                })
                
                # Closing
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎯 Closing: "
                                },
                                "annotations": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": {
                                    "content": script.get('cierre', '')
                                }
                            }
                        ]
                    }
                })
            
            # Hashtags
            if en.get('hashtags'):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🏷️ Hashtags"
                                }
                            }
                        ]
                    }
                })
                
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": en['hashtags']
                                },
                                "annotations": {
                                    "code": True
                                }
                            }
                        ]
                    }
                })
            
            # Video prompts
            if 'video_prompts' in en and en['video_prompts']:
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎥 Video Prompts"
                                }
                            }
                        ]
                    }
                })
                
                for i, prompt in enumerate(en['video_prompts'], 1):
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Video {i}: {prompt}"
                                    }
                                }
                            ]
                        }
                    })
        
        return blocks