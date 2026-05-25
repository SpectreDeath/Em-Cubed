// Workflow Designer JavaScript
class WorkflowDesigner {
    constructor() {
        this.canvas = document.getElementById('workflow-canvas');
        this.skillItems = document.querySelectorAll('.skill-item');
        this.propertiesContent = document.getElementById('properties-content');
        this.selectedStep = null;
        this.connections = [];
        this.tempConnection = null;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        
        this.init();
    }
    
    init() {
        this.loadSampleSkills();
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.updatePropertiesPanel('Select a step to view its properties');
    }
    
    loadSampleSkills() {
        // In a real implementation, this would fetch from registry
        console.log('Loading sample skills...');
    }
    
    setupEventListeners() {
        // Clear workflow
        document.getElementById('clear-workflow').addEventListener('click', () => {
            if (confirm('Are you sure you want to clear the workflow?')) {
                this.clearWorkflow();
            }
        });
        
        // Save workflow
        document.getElementById('save-workflow').addEventListener('click', () => {
            this.saveWorkflow();
        });
        
        // Load workflow
        document.getElementById('load-workflow').addEventListener('click', () => {
            this.loadWorkflow();
        });
        
        // Export workflow
        document.getElementById('export-workflow').addEventListener('click', () => {
            this.exportWorkflow();
        });
        
        // Skill search
        document.getElementById('skill-search').addEventListener('input', (e) => {
            this.filterSkills(e.target.value);
        });
        
        // Canvas click to deselect
        this.canvas.addEventListener('click', (e) => {
            if (!e.target.closest('.workflow-step') && !e.target.closest('.port')) {
                this.deselectStep();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Delete' && this.selectedStep) {
                this.removeStep(this.selectedStep);
            }
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveWorkflow();
            }
            if (e.ctrlKey && e.key === 'z') {
                e.preventDefault();
                // Undo functionality would go here
            }
        });
    }
    
    setupDragAndDrop() {
        // Make skill items draggable
        this.skillItems.forEach(item => {
            item.setAttribute('draggable', true);
            
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', item.dataset.skill);
                e.dataTransfer.effectAllowed = 'copy';
                item.classList.add('dragging');
            });
            
            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
            });
        });
        
        // Make canvas droppable
        this.canvas.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            this.canvas.classList.add('dragover');
        });
        
        this.canvas.addEventListener('dragleave', () => {
            this.canvas.classList.remove('dragover');
        });
        
        this.canvas.addEventListener('drop', (e) => {
            e.preventDefault();
            this.canvas.classList.remove('dragover');
            
            const skillId = e.dataTransfer.getData('text/plain');
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left - 100; // Center the step
            const y = e.clientY - rect.top - 50;
            
            this.addStep(skillId, x, y);
        });
        
        // Enable dragging of workflow steps
        this.canvas.addEventListener('mousedown', (e) => {
            const step = e.target.closest('.workflow-step');
            if (step && !e.target.closest('.port')) {
                this.isDragging = true;
                this.selectedStep = step;
                this.selectStep(step);
                
                const rect = step.getBoundingClientRect();
                this.dragOffset = {
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top
                };
            }
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!this.isDragging || !this.selectedStep) return;
            
            const canvasRect = this.canvas.getBoundingClientRect();
            let x = e.clientX - canvasRect.left - this.dragOffset.x;
            let y = e.clientY - canvasRect.top - this.dragOffset.y;
            
            // Keep within canvas bounds
            x = Math.max(0, Math.min(x, this.canvas.clientWidth - this.selectedStep.offsetWidth));
            y = Math.max(0, Math.min(y, this.canvas.clientHeight - this.selectedStep.offsetHeight));
            
            this.selectedStep.style.left = `${x}px`;
            this.selectedStep.style.top = `${y}px`;
            
            // Update connections
            this.updateConnectionsForStep(this.selectedStep);
        });
        
        document.addEventListener('mouseup', () => {
            if (this.isDragging) {
                this.isDragging = false;
                this.selectedStep = null;
            }
        });
    }
    
    addStep(skillId, x, y) {
        const stepId = `step-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        const step = document.createElement('div');
        step.className = 'workflow-step';
        step.id = stepId;
        step.dataset.skill = skillId;
        step.style.left = `${x}px`;
        step.style.top = `${y}px`;
        
        // Get skill name (in real implementation, this would come from registry)
        const skillName = this.getSkillName(skillId);
        
        step.innerHTML = `
            <div class="step-header">
                <h3><i class="fas fa-tasks"></i> ${skillName}</h3>
                <button class="btn-remove" title="Remove step">&times;</button>
            </div>
            <div class="step-content">
                <p>Skill: <strong>${skillId}</strong></p>
                <p>Double click to configure</p>
            </div>
            <div class="port input"></div>
            <div class="port output"></div>
        `;
        
        // Add remove button handler
        step.querySelector('.btn-remove').addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeStep(step);
        });
        
        // Add double click to configure
        step.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            this.configureStep(step);
        });
        
        // Add click to select
        step.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectStep(step);
        });
        
        // Setup ports for connections
        this.setupPorts(step);
        
        this.canvas.appendChild(step);
        this.selectStep(step);
        
        return step;
    }
    
    setupPorts(step) {
        const inputPort = step.querySelector('.port.input');
        const outputPort = step.querySelector('.port.output');
        
        // Input port - can accept connections
        inputPort.addEventListener('pointerdown', (e) => {
            e.stopPropagation();
            this.startConnection(inputPort, 'input');
        });
        
        // Output port - can start connections
        outputPort.addEventListener('pointerdown', (e) => {
            e.stopPropagation();
            this.startConnection(outputPort, 'output');
        });
        
        // Handle touch events for mobile
        inputPort.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.startConnection(inputPort, 'input');
        });
        
        outputPort.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.startConnection(outputPort, 'output');
        });
    }
    
    startConnection(port, type) {
        // Disallow connecting input to input or output to output
        if (this.tempConnection) {
            this.cancelTempConnection();
        }
        
        this.tempConnection = {
            port: port,
            type: type, // 'input' or 'output'
            step: port.closest('.workflow-step'),
            startPoint: this.getPortPosition(port)
        };
        
        // Create temporary SVG line
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'connection-line temp');
        svg.setAttribute('x1', this.tempConnection.startPoint.x);
        svg.setAttribute('y1', this.tempConnection.startPoint.y);
        svg.setAttribute('x2', this.tempConnection.startPoint.x);
        svg.setAttribute('y2', this.tempConnection.startPoint.y);
        
        this.canvas.parentElement.insertBefore(svg, this.canvas.nextSibling);
        this.tempConnection.svg = svg;
        
        // Update on mouse move
        const moveHandler = (e) => {
            if (!this.tempConnection) return;
            
            let clientX, clientY;
            if (e.type === 'mousemove') {
                clientX = e.clientX;
                clientY = e.clientY;
            } else if (e.type === 'touchmove') {
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            } else {
                return;
            }
            
            const canvasRect = this.canvas.getBoundingClientRect();
            const x = clientX - canvasRect.left;
            const y = clientY - canvasRect.top;
            
            this.tempConnection.svg.setAttribute('x2', x);
            this.tempConnection.svg.setAttribute('y2', y);
            
            // Check if we're over a valid port
            const targetPort = this.getPortAtPosition(x, y);
            if (targetPort && this.isValidConnection(this.tempConnection.port, targetPort)) {
                targetPort.classList.add('valid-target');
                this.tempConnection.targetPort = targetPort;
                this.tempConnection.svg.setAttribute('class', 'connection-line temp valid');
            } else {
                if (this.tempConnection.targetPort) {
                    this.tempConnection.targetPort.classList.remove('valid-target');
                    delete this.tempConnection.targetPort;
                }
                this.tempConnection.svg.setAttribute('class', 'connection-line temp invalid');
            }
        };
        
        const endHandler = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            if (this.tempConnection && this.tempConnection.targetPort) {
                // Complete the connection
                this.createConnection(
                    this.tempConnection.port,
                    this.tempConnection.targetPort
                );
            }
            
            this.cancelTempConnection();
        };
        
        document.addEventListener('pointermove', moveHandler);
        document.addEventListener('pointerup', endHandler);
        document.addEventListener('touchmove', moveHandler);
        document.addEventListener('touchend', endHandler);
        
        // Store handlers for cleanup
        this.tempConnection.moveHandler = moveHandler;
        this.tempConnection.endHandler = endHandler;
    }
    
    cancelTempConnection() {
        if (this.tempConnection) {
            if (this.tempConnection.targetPort) {
                this.tempConnection.targetPort.classList.remove('valid-target');
            }
            if (this.tempConnection.svg) {
                this.tempConnection.svg.remove();
            }
            if (this.tempConnection.moveHandler) {
                document.removeEventListener('pointermove', this.tempConnection.moveHandler);
                document.removeEventListener('touchmove', this.tempConnection.moveHandler);
            }
            if (this.tempConnection.endHandler) {
                document.removeEventListener('pointerup', this.tempConnection.endHandler);
                document.removeEventListener('touchend', this.tempConnection.endHandler);
            }
            this.tempConnection = null;
        }
    }
    
    getPortPosition(port) {
        const rect = port.getBoundingClientRect();
        const canvasRect = this.canvas.getBoundingClientRect();
        return {
            x: rect.left - canvasRect.left + rect.width / 2,
            y: rect.top - canvasRect.top + rect.height / 2
        };
    }
    
    getPortAtPosition(x, y) {
        const ports = document.querySelectorAll('.port:not(.temp)');
        for (const port of ports) {
            const rect = port.getBoundingClientRect();
            const canvasRect = this.canvas.getBoundingClientRect();
            const portCenterX = rect.left - canvasRect.left + rect.width / 2;
            const portCenterY = rect.top - canvasRect.top + rect.height / 2;
            
            const distance = Math.sqrt(
                Math.pow(x - portCenterX, 2) + 
                Math.pow(y - portCenterY, 2)
            );
            
            if (distance < 20) { // 20px tolerance
                return port;
            }
        }
        return null;
    }
    
    isValidConnection(port1, port2) {
        // Can't connect to same port
        if (port1 === port2) return false;
        
        // Must be from different steps
        const step1 = port1.closest('.workflow-step');
        const step2 = port2.closest('.workflow-step');
        if (step1 === step2) return false;
        
        // Input can only connect to output and vice versa
        const type1 = port1.classList.contains('input') ? 'input' : 'output';
        const type2 = port2.classList.contains('input') ? 'input' : 'output';
        
        return type1 !== type2;
    }
    
    createConnection(startPort, endPort) {
        // Determine which is output and which is input
        const outputPort = startPort.classList.contains('output') ? startPort : endPort;
        const inputPort = startPort.classList.contains('input') ? startPort : endPort;
        
        const outputStep = outputPort.closest('.workflow-step');
        const inputStep = inputPort.closest('.workflow-step');
        
        // Check if connection already exists (avoid duplicates)
        const existing = this.connections.find(conn => 
            conn.outputStep === outputStep && 
            conn.inputStep === inputStep
        );
        
        if (existing) {
            // Update existing connection
            existing.outputPort = outputPort;
            existing.inputPort = inputPort;
        } else {
            // Create new connection
            this.connections.push({
                outputStep: outputStep,
                inputStep: inputStep,
                outputPort: outputPort,
                inputPort: inputPort
            });
        }
        
        // Update port styling
        outputPort.classList.add('connected');
        inputPort.classList.add('connected');
        
        // Render the connection
        this.renderConnection(this.connections[this.connections.length - 1]);
        
        // Update properties panel if either step is selected
        if (this.selectedStep === outputStep || this.selectedStep === inputStep) {
            this.updatePropertiesPanel(this.selectedStep);
        }
    }
    
    renderConnection(connection) {
        // Remove any existing SVG for this connection
        const existingSvg = this.canvas.parentElement.querySelector(
            `.connection-line[data-output="${connection.outputStep.id}"][data-input="${connection.inputStep.id}"]`
        );
        if (existingSvg) {
            existingSvg.remove();
        }
        
        // Create new SVG line
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'connection-line');
        svg.setAttribute('data-output', connection.outputStep.id);
        svg.setAttribute('data-input', connection.inputStep.id);
        
        const startPoint = this.getPortPosition(connection.outputPort);
        const endPoint = this.getPortPosition(connection.inputPort);
        
        svg.setAttribute('x1', startPoint.x);
        svg.setAttribute('y1', startPoint.y);
        svg.setAttribute('x2', endPoint.x);
        svg.setAttribute('y2', endPoint.y);
        
        // Add some curvature for better visuals
        const midX = (startPoint.x + endPoint.x) / 2;
        const midY = (startPoint.y + endPoint.y) / 2;
        const controlOffset = 50;
        
        svg.setAttribute('d', `M ${startPoint.x},${startPoint.y} C ${midX - controlOffset},${startPoint.y} ${midX + controlOffset},${endPoint.y} ${endPoint.x},${endPoint.y}`);
        svg.setAttribute('fill', 'none');
        
        this.canvas.parentElement.insertBefore(svg, this.canvas.nextSibling);
    }
    
    updateConnectionsForStep(step) {
        // Update all connections that involve this step
        this.connections.forEach(connection => {
            if (connection.outputStep === step || connection.inputStep === step) {
                // Find the SVG element
                const svg = this.canvas.parentElement.querySelector(
                    `.connection-line[data-output="${connection.outputStep.id}"][data-input="${connection.inputStep.id}"]`
                );
                
                if (svg) {
                    const startPoint = this.getPortPosition(connection.outputPort);
                    const endPoint = this.getPortPosition(connection.inputPort);
                    
                    const midX = (startPoint.x + endPoint.x) / 2;
                    const midY = (startPoint.y + endPoint.y) / 2;
                    const controlOffset = 50;
                    
                    svg.setAttribute('d', `M ${startPoint.x},${startPoint.y} C ${midX - controlOffset},${startPoint.y} ${midX + controlOffset},${endPoint.y} ${endPoint.x},${endPoint.y}`);
                }
            }
        });
    }
    
    selectStep(step) {
        // Deselect previously selected step
        if (this.selectedStep) {
            this.selectedStep.classList.remove('selected');
        }
        
        // Select new step
        this.selectedStep = step;
        step.classList.add('selected');
        
        // Update properties panel
        this.updatePropertiesPanel(step);
    }
    
    deselectStep() {
        if (this.selectedStep) {
            this.selectedStep.classList.remove('selected');
            this.selectedStep = null;
            this.updatePropertiesPanel('Select a step to view its properties');
        }
    }
    
    removeStep(step) {
        // Remove connections involving this step
        this.connections = this.connections.filter(conn => 
            conn.outputStep !== step && conn.inputStep !== step
        );
        
        // Remove connection SVGs
        this.connections.forEach(connection => {
            const svg = this.canvas.parentElement.querySelector(
                `.connection-line[data-output="${connection.outputStep.id}"][data-input="${connection.inputStep.id}"]`
            );
            if (svg) svg.remove();
        });
        
        // Remove the step element
        step.remove();
        
        // Clear selection if this was the selected step
        if (this.selectedStep === step) {
            this.selectedStep = null;
            this.updatePropertiesPanel('Select a step to view its properties');
        }
    }
    
    configureStep(step) {
        // In a real implementation, this would open a modal to configure the step
        alert(`Configuration for ${this.getSkillName(step.dataset.skill)} would go here\n\nIn a full implementation, this would allow setting:\n- Input/output mappings\n- Conditions\n- Timeouts\n- Retry policies\n- Error handling`);
        this.selectStep(step);
    }
    
    getSkillName(skillId) {
        // Map skill IDs to display names
        const skillNames = {
            'python_calculator': 'Python Calculator',
            'basic-stats': 'Basic Statistics',
            'shell-executor': 'Shell Executor',
            'file-processor': 'File Processor',
            'llm-processor': 'LLM Processor',
            'text-analyzer': 'Text Analyzer'
        };
        return skillNames[skillId] || skillId;
    }
    
    filterSkills(query) {
        query = query.toLowerCase().trim();
        document.querySelectorAll('.skill-item').forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(query) ? 'flex' : 'none';
        });
    }
    
    clearWorkflow() {
        // Remove all steps
        this.canvas.querySelectorAll('.workflow-step').forEach(step => step.remove());
        
        // Remove all connections
        this.connections.forEach(connection => {
            const svg = this.canvas.parentElement.querySelector(
                `.connection-line[data-output="${connection.outputStep.id}"][data-input="${connection.inputStep.id}"]`
            );
            if (svg) svg.remove();
        });
        
        this.connections = [];
        
        // Clear selection
        this.deselectStep();
    }
    
    saveWorkflow() {
        // In a real implementation, this would save to localStorage or backend
        const workflowData = {
            steps: Array.from(this.canvas.querySelectorAll('.workflow-step')).map(step => ({
                id: step.id,
                skill: step.dataset.skill,
                position: {
                    x: parseFloat(step.style.left),
                    y: parseFloat(step.style.top)
                }
            })),
            connections: this.connections.map(conn => ({
                output: conn.outputStep.id,
                input: conn.inputStep.id
            }))
        };
        
        // For demo, just show the data
        alert('Workflow saved!\n\nIn a real implementation, this would be saved to storage.\n\nWorkflow data:\n' + JSON.stringify(workflowData, null, 2));
        
        // Also save to localStorage for demo purposes
        try {
            localStorage.setItem('em-cubed-workflow', JSON.stringify(workflowData));
        } catch (e) {
            console.warn('Could not save to localStorage:', e);
        }
    }
    
    loadWorkflow() {
        // In a real implementation, this would load from localStorage or backend
        try {
            const saved = localStorage.getItem('em-cubed-workflow');
            if (saved) {
                const workflowData = JSON.parse(saved);
                
                // Clear current workflow
                this.clearWorkflow();
                
                // Load steps
                workflowData.steps.forEach(stepData => {
                    const step = this.addStep(stepData.skill, stepData.position.x, stepData.position.y);
                    step.id = stepData.id; // Restore original ID
                });
                
                // Load connections
                workflowData.connections.forEach(connData => {
                    const outputStep = this.canvas.querySelector(`#${connData.output}`);
                    const inputStep = this.canvas.querySelector(`#${connData.input}`);
                    
                    if (outputStep && inputStep) {
                        const outputPort = outputStep.querySelector('.port.output');
                        const inputPort = inputStep.querySelector('.port.input');
                        
                        if (outputPort && inputPort) {
                            this.createConnection(outputPort, inputPort);
                        }
                    }
                });
                
                alert('Workflow loaded from local storage!');
            } else {
                // Load sample workflow for demo
                this.loadSampleWorkflow();
            }
        } catch (e) {
            console.error('Error loading workflow:', e);
            // Load sample workflow on error
            this.loadSampleWorkflow();
        }
    }
    
    loadSampleWorkflow() {
        this.clearWorkflow();
        
        // Add a sample workflow: Calculator -> Stats -> LLM Processor
        const calc = this.addStep('python_calculator', 100, 100);
        const stats = this.addStep('basic-stats', 400, 100);
        const llm = this.addStep('llm-processor', 700, 100);
        
        // Connect them
        const calcOutput = calc.querySelector('.port.output');
        const statsInput = stats.querySelector('.port.input');
        const statsOutput = stats.querySelector('.port.output');
        const llmInput = llm.querySelector('.port.input');
        
        this.createConnection(calcOutput, statsInput);
        this.createConnection(statsOutput, llmInput);
        
        // Select first step
        this.selectStep(calc);
        
        alert('Loaded sample workflow: Calculator → Statistics → LLM Processor');
    }
    
    exportWorkflow() {
        const workflowDefinition = {
            name: 'Exported Workflow',
            description: 'Workflow created with Em-Cubed Visual Workflow Designer',
            steps: [],
            connections: []
        };
        
        // Export steps
        this.canvas.querySelectorAll('.workflow-step').forEach(step => {
            workflowDefinition.steps.push({
                id: step.id,
                skill_id: step.dataset.skill,
                name: this.getSkillName(step.dataset.skill),
                input_mapping: {}, // Would be configured in properties
                output_mapping: {}, // Would be configured in properties
                dependencies: [] // Would be derived from connections
            });
        });
        
        // Export connections as dependencies
        this.connections.forEach(conn => {
            const inputStep = conn.inputStep.closest('.workflow-step');
            if (inputStep) {
                // Find the step definition
                const stepDef = workflowDefinition.steps.find(s => s.id === inputStep.id);
                if (stepDef) {
                    // Add the output step as a dependency
                    const depId = conn.outputStep.id;
                    if (!stepDef.dependencies.includes(depId)) {
                        stepDef.dependencies.push(depId);
                    }
                }
            }
        });
        
        // Convert to YAML-like format for display
        const yamlText = this.toYamlLike(workflowDefinition);
        
        // Show in a popup or allow download
        const blob = new Blob([yamlText], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'workflow.skill.md';
        a.click();
        URL.revokeObjectURL(url);
        
        alert('Workflow exported as YAML!\n\nThe file has been downloaded as workflow.skill.md\n\nYou can import this into your Em-Cubed skills directory.');
    }
    
    toYamlLike(obj) {
        // Simple YAML-like conversion for display
        const indent = '  ';
        const toIndent = (str, level) => {
            return str.split('\n').map(line => indent.repeat(level) + line).join('\n');
        };
        
        let result = '---\n';
        result += `name: ${obj.name}\n`;
        result += `description: ${obj.description || ''}\n`;
        result += 'steps:\n';
        
        obj.steps.forEach((step, index) => {
            result += `${indent}- id: ${step.id}\n`;
            result += `${indent}  name: "${step.name}"\n`;
            result += `${indent}  skill_id: ${step.skill_id}\n`;
            result += `${indent}  input_mapping: {}\n`; // Simplified
            result += `${indent}  output_mapping: {}\n`; // Simplified
            result += `${indent}  dependencies: [${step.dependencies.map(d => `"${d}"`).join(', ')}]\n`;
        });
        
        result += '---\n\n';
        result += '# Workflow description goes here\n';
        result += '# This workflow was created with the Em-Cubed Visual Workflow Designer\n';
        
        return result;
    }
}

// Initialize the workflow designer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.workflowDesigner = new WorkflowDesigner();
});