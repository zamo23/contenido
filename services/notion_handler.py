from notion_client import Client
from config.config import Config

class NotionHandler:
    """Handles Notion API operations for content management."""

    def __init__(self):
        self.client = Client(auth=Config.get_notion_token())
        self.database_id = Config.get_notion_database_id()
        self.database_properties = self._get_database_properties()
        self.title_property_name = self._get_title_property_name()

    def _get_database_properties(self):
        """Get all properties of the database."""
        try:
            database = self.client.databases.retrieve(database_id=self.database_id)
            return database['properties']
        except Exception as e:
            print(f"Error retrieving database properties: {e}")
            return {}

    def _get_title_property_name(self):
        """Get the name of the title property in the database."""
        for prop_name, prop_info in self.database_properties.items():
            if prop_info['type'] == 'title':
                return prop_name
        return 'Name'  # fallback

    def create_content_page(self, ideas: dict, category: str):
        """Create a new page in Notion with the generated content."""
        # Get the title from the Spanish version (assuming it's the primary)
        page_title = ideas.get('es', {}).get('title', f'Content for {category}')
        
        # Create page properties
        properties = {
            self.title_property_name: {
                "title": [
                    {
                        "text": {
                            "content": page_title
                        }
                    }
                ]
            }
        }

        # If there's an "Área" property, set the category there
        if 'Área' in self.database_properties:
            prop_type = self.database_properties['Área']['type']
            if prop_type == 'multi_select':
                properties['Área'] = {
                    "multi_select": [
                        {
                            "name": category
                        }
                    ]
                }
            elif prop_type == 'select':
                properties['Área'] = {
                    "select": {
                        "name": category
                    }
                }
            else:
                # Fallback to rich_text if it's not select/multi_select
                properties['Área'] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": category
                            }
                        }
                    ]
                }

        # Set an icon for the page
        icon = {
            "type": "emoji",
            "emoji": "📝"
        }

        # Generate blocks
        blocks = self._create_styled_guion_blocks(ideas)

        # Create the page
        page = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
            icon=icon,
            children=blocks
        )
        return page

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

            # Video prompts (ES) - justo después del guion en español
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

            # Español - links de imágenes y videos de Pexels
            if 'pexels_images' in es and es['pexels_images']:
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🖼️ Imágenes sugeridas (Pexels)"
                                }
                            }
                        ]
                    }
                })
                for img_url in es['pexels_images']:
                    # Add the image block
                    blocks.append({
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "external",
                            "external": {
                                "url": img_url
                            }
                        }
                    })
                    # Add the direct link below
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Link directo: {img_url}",
                                        "link": {"url": img_url}
                                    },
                                    "annotations": {
                                        "code": True
                                    }
                                }
                            ]
                        }
                    })
            if 'pexels_videos' in es and es['pexels_videos']:
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎬 Videos sugeridos (Pexels)"
                                }
                            }
                        ]
                    }
                })
                for vid_url in es['pexels_videos']:
                    # Add the video block
                    blocks.append({
                        "object": "block",
                        "type": "video",
                        "video": {
                            "type": "external",
                            "external": {
                                "url": vid_url
                            }
                        }
                    })
                    # Add the direct link below
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Link directo: {vid_url}",
                                        "link": {"url": vid_url}
                                    },
                                    "annotations": {
                                        "code": True
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

            # Video prompts (EN) - justo después del guion en inglés
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

            # Inglés - links de imágenes y videos de Pexels
            if 'pexels_images' in en and en['pexels_images']:
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🖼️ Suggested images (Pexels)"
                                }
                            }
                        ]
                    }
                })
                for img_url in en['pexels_images']:
                    # Add the image block
                    blocks.append({
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "external",
                            "external": {
                                "url": img_url
                            }
                        }
                    })
                    # Add the direct link below
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Direct link: {img_url}",
                                        "link": {"url": img_url}
                                    },
                                    "annotations": {
                                        "code": True
                                    }
                                }
                            ]
                        }
                    })
            if 'pexels_videos' in en and en['pexels_videos']:
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "🎬 Suggested videos (Pexels)"
                                }
                            }
                        ]
                    }
                })
                for vid_url in en['pexels_videos']:
                    # Add the video block
                    blocks.append({
                        "object": "block",
                        "type": "video",
                        "video": {
                            "type": "external",
                            "external": {
                                "url": vid_url
                            }
                        }
                    })
                    # Add the direct link below
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Direct link: {vid_url}",
                                        "link": {"url": vid_url}
                                    },
                                    "annotations": {
                                        "code": True
                                    }
                                }
                            ]
                        }
                    })

        return blocks
