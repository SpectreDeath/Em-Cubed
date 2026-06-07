import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    // Resolve the Python interpreter: prefer the workspace's configured
    // interpreter (e.g. from the Python extension), then fall back to PATH.
    const pythonConfig = vscode.workspace.getConfiguration('python');
    const pythonPath: string =
        pythonConfig.get<string>('defaultInterpreterPath') ||
        pythonConfig.get<string>('pythonPath') ||
        process.env.PYTHON_PATH ||
        'python';

    // skill_lsp.py lives at <extension-root>/lsp/src/skill_lsp.py.
    // context.extensionPath is always the extension root, so this resolves
    // correctly both when running from the .vsix bundle and in dev mode (F5).
    const serverModule = context.asAbsolutePath(
        path.join('lsp', 'src', 'skill_lsp.py')
    );

    const serverOptions: ServerOptions = {
        command: pythonPath,
        args: ['-u', serverModule],
    };

    const clientOptions: LanguageClientOptions = {
        // Activate for files that match *.skill.md or SKILL.md
        documentSelector: [
            { scheme: 'file', language: 'skill' },
            { scheme: 'file', pattern: '**/{SKILL,*.skill}.md' },
        ],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher(
                '**/{SKILL,*.skill}.md'
            ),
        },
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