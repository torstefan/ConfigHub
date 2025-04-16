class FrontendLogger {
    constructor() {
        this.logs = [];
        this.logBuffer = [];
        this.bufferSize = 50; // Number of logs to buffer before sending
        this.logLevel = 'debug'; // debug, info, warn, error
        
        // Set up periodic log upload
        setInterval(() => this.uploadLogs(), 10000); // Upload every 10 seconds if there are logs
    }

    log(level, component, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            component,
            message,
            data: data ? JSON.stringify(data) : null,
            url: window.location.href,
            userAgent: navigator.userAgent
        };

        this.logs.push(logEntry);
        this.logBuffer.push(logEntry);
        console.log(`[${timestamp}] [${level.toUpperCase()}] [${component}] ${message}`, data || '');

        if (this.logBuffer.length >= this.bufferSize) {
            this.uploadLogs();
        }
    }

    debug(component, message, data = null) {
        if (this.shouldLog('debug')) {
            this.log('debug', component, message, data);
        }
    }

    info(component, message, data = null) {
        if (this.shouldLog('info')) {
            this.log('info', component, message, data);
        }
    }

    warn(component, message, data = null) {
        if (this.shouldLog('warn')) {
            this.log('warn', component, message, data);
        }
    }

    error(component, message, data = null) {
        if (this.shouldLog('error')) {
            this.log('error', component, message, data);
        }
    }

    shouldLog(level) {
        const levels = ['debug', 'info', 'warn', 'error'];
        const currentLevelIndex = levels.indexOf(this.logLevel);
        const messageLevelIndex = levels.indexOf(level);
        return messageLevelIndex >= currentLevelIndex;
    }

    async uploadLogs() {
        if (this.logBuffer.length === 0) return;

        const logsToUpload = [...this.logBuffer];
        this.logBuffer = [];

        try {
            // Upload each log entry individually
            for (const log of logsToUpload) {
                const response = await fetch('/api/log', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        level: log.level,
                        message: `[${log.component}] ${log.message}${log.data ? ` - Data: ${log.data}` : ''}`
                    })
                });

                if (!response.ok) {
                    console.error('Failed to upload log:', response.statusText);
                    // Put this log back in buffer
                    this.logBuffer.push(log);
                }
            }
        } catch (error) {
            console.error('Error uploading logs:', error);
            // Put all logs back in buffer
            this.logBuffer = [...logsToUpload, ...this.logBuffer];
        }
    }

    setLogLevel(level) {
        this.logLevel = level;
    }
}

// Create global logger instance
window.logger = new FrontendLogger(); 