# P4 Automation Maintenance Guide

## Regular Maintenance Tasks

### Daily Tasks
1. **Check Session Status**
   ```python
   from app.automation.auth.session_manager import SessionManager
   manager = SessionManager(storage_path)
   print(manager.is_session_valid())
   ```

2. **Monitor Memory Usage**
   ```python
   from app.automation.utils.memory_optimizer import MemoryOptimizer
   optimizer = MemoryOptimizer()
   print(await optimizer.check_memory_usage())
   ```

3. **Review Error Logs**
   ```bash
   tail -f ~/.notebooklm/logs/*.log
   ```

### Weekly Tasks
1. **Clean Up Old Screenshots**
   ```bash
   find ~/.notebooklm/screenshots -mtime +7 -delete
   ```

2. **Clean Up Expired Cache**
   ```python
   from app.automation.utils.memory_optimizer import CacheManager
   cache = CacheManager()
   cache.cleanup_expired()
   ```

3. **Update Selectors** (if UI changes)
   - Run selector auto-detection
   - Update selector registry
   - Test selectors

### Monthly Tasks
1. **Update Playwright**
   ```bash
   pip install --upgrade playwright
   playwright install chromium
   ```

2. **Review Performance Metrics**
   - Check response times
   - Review memory usage trends
   - Analyze error rates

3. **Backup Configuration**
   ```bash
   tar -czf backup_$(date +%Y%m%d).tar.gz ~/.notebooklm/
   ```

## Configuration Management

### Browser Settings
- Location: `app/automation/config/settings.py`
- Key settings:
  - `HEADLESS`: Run browser in headless mode
  - `SLOW_MO`: Slow down operations for debugging
  - `VIEWPORT_WIDTH/HEIGHT`: Browser window size

### Profile Management
- Location: `~/.notebooklm/profiles/`
- Each profile contains:
  - `storage_state.json`: Session data
  - `browser_profile/`: Browser data

### Selector Configuration
- Location: `app/automation/utils/selector_registry.py`
- Update when NotebookLM UI changes

## Monitoring

### Health Checks
```python
from app.automation.monitoring.health_check import HealthCheck
health = HealthCheck()
print(await health.run_checks())
```

### Operation Logging
```python
from app.automation.monitoring.operation_logger import OperationLogger
logger = OperationLogger()
logger.log_operation("test", "create_notebook", "success")
```

### Alerting
```python
from app.automation.monitoring.alerting import AlertingSystem
alerting = AlertingSystem()
await alerting.check_alerts(metrics)
```

## Performance Optimization

### Memory Management
- Limit concurrent browser sessions
- Close unused contexts
- Run periodic cleanup

### Caching
- Cache frequently accessed data
- Set appropriate TTL
- Monitor cache hit rates

### Rate Limiting
- Respect API rate limits
- Implement exponential backoff
- Monitor request frequency

## Security

### Session Management
- Store sessions securely
- Rotate session tokens
- Monitor for unauthorized access

### API Keys
- Never commit API keys
- Use environment variables
- Rotate keys regularly

### Data Protection
- Encrypt sensitive data
- Limit data retention
- Secure file storage

## Backup and Recovery

### Backup Strategy
1. Configuration files
2. Session data
3. Logs and screenshots
4. Database (if applicable)

### Recovery Steps
1. Identify failure point
2. Restore from backup
3. Verify configuration
4. Test functionality

## Support

### Documentation
- API Documentation: `docs/API.md`
- Architecture: `docs/ARCHITECTURE.md`
- Setup Guide: `docs/SETUP.md`

### Issue Tracking
- Report bugs via GitHub Issues
- Include error logs and screenshots
- Provide reproduction steps

### Contact
- Development Team
- DevOps Team
- Project Lead
