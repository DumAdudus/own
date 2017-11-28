# -*- coding: utf-8 -*-
from IPython.terminal.prompts import Prompts, Token
import os


class OwnPrompt(Prompts):

    def inprompt_tokens(self, cli=None):  # sample
        return [(Token, os.getcwd()),
                (Token.Prompt, ' >>>')]

    def in_prompt_tokens(self, cli=None):   # custom
        path = os.path.basename(os.getcwd())
        return [
            (Token.PromptNum, str(self.shell.execution_count)),
            (Token.Prompt, ':'),
            (Token.PromptNum, '~/'+path),
            (Token.Prompt, '$ '),
        ]

    def in_prompt_tokens(self, cli=None):   # custom
        path = os.path.basename(os.getcwd())
        return [
            (Token.PromptNum, '~/'+path),
            (Token.Prompt, ' >'),
            (Token.PromptNum, str(self.shell.execution_count)),
            (Token.Prompt, '<: '),
        ]

    def out_prompt_tokens(self):
        return [
            (Token.OutPrompt, '>'),
            (Token.OutPromptNum, str(self.shell.execution_count)),
            (Token.OutPrompt, '< '),
        ]

ip=get_ipython()
ip.prompts=OwnPrompt(ip)
