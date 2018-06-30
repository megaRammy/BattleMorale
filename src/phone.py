LINE_SPACING = -2

import pygame
from collections import namedtuple

BubbleSprites = namedtuple("BubbleSprites","top_left, top_right, bottom_left, bottom_right, top, bottom, left, right, center")

class Message:
    font = None
    sprites = None
    margin_left = None
    margin_right = None
    margin_top = None
    margin_bottom = None
    max_text_width = None

    def splitText(self,text):
        self.lines = []
        self.line_space = self.font.size("Tg")[1] + LINE_SPACING
        self.text_height = -LINE_SPACING
        self.text_width = 0
        while text:
            i = 1
            # determine maximum width of line
            line_width = self.font.size(text[:i])[0]
            while line_width < self.max_text_width and i < len(text):
                i += 1
            # if we've wrapped the text, then adjust the wrap to the last word      
            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1

            self.lines.append(text[:i])
            self.text_height += self.line_space
            if self.text_width < line_width:
                self.text_width = line_width
            text = text[i:]
    
    def pre_render(self):
        total_width = self.text_width + self.margin_left + self.margin_right
        total_height = self.text_height + self.margin_top + self.margin_bottom

        x1,y1 = self.sprites.top_left.get_size()
        right_width,bottom_height = self.sprites.bottom_right.get_size()
        x2 = total_width-right_width
        y2 = total_height-bottom_height

        surface = pygame.Surface((total_width,total_height))

        surface.blit(self.sprites.top_left,(0,0))
        surface.blit(self.sprites.top_right,(x2,0))
        surface.blit(self.sprites.bottom_left,(0,y2))
        surface.blit(self.sprites.bottom_right,(x1,x2))

        top_subsurface = surface.subsurface((x1,0,x2-x1,y1))
        bottom_subsurface = surface.subsurface((x1,y2,x2-x1,bottom_height))
        left_subsurface = surface.subsurface((0,y1,x1,y2-y1))
        right_subsurface = surface.subsurface((x2,y1,right_width,y2-y1))
        center_subsurface = surface.subsurface((x1,y1,x2-x1,y2-y1))

        pygame.transform.scale(self.sprites.top,top_subsurface.get_size(),top_subsurface)
        pygame.transform.scale(self.sprites.bottom,bottom_subsurface.get_size(),bottom_subsurface)
        pygame.transform.scale(self.sprites.left,left_subsurface.get_size(),left_subsurface)
        pygame.transform.scale(self.sprites.right,right_subsurface.get_size(),right_subsurface)
        pygame.transform.scale(self.sprites.center,center_subsurface.get_size(),center_subsurface)

        y = self.margin_top
        for line in self.lines:
            textRender = self.font.render(line,False,(self.margin_left,y),self.color)
            surface.blit(textRender,(self.margin_right,y))
            y += self.line_space

        return surface
    
    @classmethod
    def factory(cls, name, **options):
        type(name, (cls,), options)

class Phone:
    def __init__(self,font,phone_sprite,bubbles_bottom,pc_bubble_config,npc_bubble_config,max_text_width):
        self.PcMessage = Message.factory("PcMessage"
            font = font
            sprites = pc_bubble_config.sprites
            margin_left = pc_bubble_config.margin_left
            margin_right = pc_bubble_config.margin_right
            margin_top = pc_bubble_config.margin_top
            margin_bottom = pc_bubble_config.margin_bottom
            max_text_width = max_text_width
        )

        self.NpcMessage = Message.factory("NpcMessage"
            font = font
            sprites = npc_bubble_config.sprites
            margin_left = npc_bubble_config.margin_left
            margin_right = npc_bubble_config.margin_right
            margin_top = npc_bubble_config.margin_top
            margin_bottom = npc_bubble_config.margin_bottom
            max_text_width = max_text_width
        )

        self.sprite = phone_sprite
        self.bubbles_bottom = bubbles_bottom
        self.bubbles_left = 0

        self.x = 0
        self.y = 0

        self.messages = []
        self.options = []
        self.dirty = True

    def add_message(self, text, type):
        self.messages.append(NpcMessage)

    def add_pc_choices(self, choices):
        self.options = [PcMessage(text,key) for (key,text) in choices.items()]

    def all_renderable_messages(self):
        yield from self.options[::-1]
        yield from self.messages[::-1]

    def render(self, surface):
        if not self.dirty:
            return
        surface.blit(self.phone_sprite,(self.x,self.y))
        bubble_y = self.bubbles_bottom

        for message in self.all_renderable_messages():
            height = message.surface.get_size()[1]
            bubble_y -= height
            if bubble_y < 0:
                break
            surface.blit(message.surface,(self.x+self.bubbles_left, self.y+self.bubbles_bottom)) 