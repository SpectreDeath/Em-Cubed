import * as path from 'path';
import * as fs from 'fs';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    // The server is implemented in Python. We spawn it as a subprocess
    const pythonPath = process.env.PYTHON_PATH || 'python';
    const serverModule = context.asAbsolutePath(
        path.join('lsp', 'src', 'skill_lsp.py')
    );

    const serverOptions: ServerOptions = {
        command: pythonPath,
        args: ['-u', serverModule],
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'skill' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.{skill.md,SKILL.md}')
        }
    };

    client = new LanguageClient(
        'em-cubed-skill-lsp',
        'Em-Cubed Skill Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    return client?.stop();
}