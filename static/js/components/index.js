/**
 * Component Loader
 * 
 * Loads and initializes all UI components for Bhanjyang Cooperative
 */

// Component registry
const ComponentRegistry = {
    components: new Map(),
    
    register(name, componentClass) {
        this.components.set(name, componentClass);
    },
    
    get(name) {
        return this.components.get(name);
    },
    
    initialize(selector, componentName, options = {}) {
        const elements = document.querySelectorAll(selector);
        const ComponentClass = this.get(componentName);
        
        if (!ComponentClass) {
            console.warn(`Component ${componentName} not found`);
            return [];
        }
        
        return Array.from(elements).map(element => {
            return new ComponentClass(element, options);
        });
    }
};

// Register all components
ComponentRegistry.register('FormField', FormField);
ComponentRegistry.register('FileUpload', FileUpload);
ComponentRegistry.register('StatCard', StatCard);
ComponentRegistry.register('Toast', Toast);
ComponentRegistry.register('Modal', Modal);

// Auto-initialize components on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize form fields
    ComponentRegistry.initialize('.form-field', 'FormField');
    
    // Initialize file uploads
    ComponentRegistry.initialize('.file-upload', 'FileUpload');
    
    // Initialize stat cards
    ComponentRegistry.initialize('.stat-card', 'StatCard');
    
    // Initialize modals
    ComponentRegistry.initialize('.modal', 'Modal');
    
    // Initialize toast system
    Toast.getInstance();
    
    console.log('Bhanjyang UI Components initialized');
});

// Export for global use
window.ComponentRegistry = ComponentRegistry;
