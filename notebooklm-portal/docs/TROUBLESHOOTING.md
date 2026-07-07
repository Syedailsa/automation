# P4 Automation Troubleshooting Guide

## Common Issues and Solutions

### 1. Browser Launch Failures

**Symptom:** `Failed to initialize browser`

**Solutions:**
- Ensure Playwright is installed: `pip install playwright`
- Install browsers: `playwright install chromium`
- Check if another browser instance is running
- Verify system requirements (Chrome/Chromium)

### 2. Session Authentication Failures

**Symptom:** `Session expired` or `Login required`

**Solutions:**
- Clear browser profile: `rm -rf ~/.notebooklm/profiles/default/`
- Re-login manually: `python -m app.automation.main --login`
- Check session file exists: `ls ~/.notebooklm/profiles/default/`

### 3. Selector Not Found

**Symptom:** `Element not found` or `Selector timeout`

**Solutions:**
- Update selectors in `utils/selector_registry.py`
- Use selector fallback logic
- Check if UI has changed
- Run selector auto-detection

### 4. Rate Limiting Issues

**Symptom:** `Rate limit exceeded` or `Too many requests`

**Solutions:**
- Increase delays between operations
- Check `resilience/rate_limiter.py` settings
- Implement exponential backoff
- Monitor request frequency

### 5. Memory Usage Issues

**Symptom:** `Out of memory` or `Process killed`

**Solutions:**
- Enable memory monitoring
- Run cleanup: `await optimizer.cleanup_memory()`
- Reduce concurrent sessions
- Close unused browser contexts

### 6. API Connection Failures

**Symptom:** `Connection refused` or `API timeout`

**Solutions:**
- Verify FastAPI server is running
- Check API URL configuration
- Verify network connectivity
- Check firewall settings

### 7. File Upload Failures

**Symptom:** `File upload failed` or `Invalid file type`

**Solutions:**
- Check file size limits
- Verify file type is supported
- Ensure file exists at specified path
- Check disk space

### 8. WebSocket Connection Issues

**Symptom:** `WebSocket connection failed`

**Solutions:**
- Verify WebSocket endpoint is running
- Check authentication tokens
- Verify network connectivity
- Check for proxy issues

## Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Log Files

- Application logs: `~/.notebooklm/logs/`
- Error screenshots: `~/.notebooklm/screenshots/`
- Session files: `~/.notebooklm/profiles/`

## Getting Help

1. Check this troubleshooting guide
2. Review error messages in logs
3. Check GitHub issues
4. Contact development team
