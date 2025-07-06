# Background Campaign Processing

MessageHub now supports hybrid background/foreground campaign processing, allowing you to run email and SMS campaigns independently of the main application.

## Features

### 🚀 Background Processing
- **Independent execution**: Campaigns run even when the main app is closed
- **Persistent logging**: All activity is logged to files for review
- **Status tracking**: Real-time status updates in the database
- **Process management**: Start, stop, and monitor campaigns
- **Auto-recovery**: Campaigns resume on app restart

### 👀 Foreground Processing  
- **Real-time monitoring**: Live progress display
- **Interactive control**: Pause, resume, or stop during execution
- **Immediate feedback**: See results as they happen
- **Traditional workflow**: Familiar email campaign wizard

## How to Use

### Launching Campaigns

1. **Create a campaign** using the standard email/SMS campaign wizard
2. **Select the campaign** from the campaign list
3. **Click "🚀 Launch Campaign"** to open the launcher dialog
4. **Choose your processing mode**:
   - **Background**: Independent processing, app can be closed
   - **Foreground**: Interactive monitoring, app stays open

### Monitoring Background Campaigns

- **Individual monitoring**: Use "📊 Monitor" button on campaign lists
- **Global overview**: Access "🖥️ Background Jobs" from the sidebar
- **Real-time updates**: Status refreshes automatically every 3-5 seconds

### Managing Background Jobs

From the **Background Jobs** manager, you can:
- View all running campaigns
- Stop individual campaigns
- Monitor progress and logs
- Clean up completed job records

## Background Processing Architecture

### Components

1. **`campaign_processor.py`**: Standalone background processor script
2. **`services/background_jobs.py`**: Job management service
3. **`features/campaign_launcher.py`**: Launch options UI
4. **`features/background_manager.py`**: Global job management UI

### Database Schema

New tables and columns for tracking:
- Campaign status (`draft`, `running`, `completed`, `failed`, `stopped`)
- Background job records with PID tracking
- Enhanced history with personalized content
- Last updated timestamps and processing details

### File Structure

```
logs/                          # Campaign processing logs
pids/                          # Process ID files for tracking
campaign_processor_email_*.log # Individual campaign logs
campaign_processor_sms_*.log   # SMS campaign logs
```

## Configuration

### Email Providers
- **SMTP**: Gmail, Outlook, custom servers
- **SendGrid**: API key-based sending
- **Amazon SES**: AWS credentials required

### SMS Providers  
- **Twilio**: Account SID, Auth Token, Phone Number
- **AWS SNS**: AWS credentials for direct SMS

## Error Handling

- **Graceful shutdown**: SIGTERM/SIGINT signal handling
- **Process monitoring**: Automatic cleanup of stale processes
- **Error logging**: Detailed error messages in logs and database
- **Retry logic**: Built-in delays to avoid rate limiting

## Security

- **No sensitive data in logs**: Personal info is handled securely
- **PID file management**: Automatic cleanup on process termination
- **Database locking**: SQLite transactions for data consistency
- **Process isolation**: Background jobs run independently

## Troubleshooting

### Common Issues

1. **Campaign won't start**: Check email/SMS provider settings
2. **Process not found**: Use Background Jobs manager to clean up stale records
3. **Permission errors**: Ensure write access to logs/ and pids/ directories
4. **Rate limiting**: Default delays are built-in, but may need adjustment

### Logs Location

- **Individual campaigns**: `campaign_processor_[type]_[id].log`
- **Application logs**: Standard application logging
- **Error tracking**: Database `background_jobs` table

### Monitoring Tips

- Use auto-refresh in Background Jobs manager
- Check processing details for progress information
- Monitor log files for detailed error messages
- Use the individual campaign monitor for real-time updates

## Benefits

### For Users
- **Uninterrupted workflow**: Continue working while campaigns run
- **Reliable processing**: Campaigns complete even if app crashes
- **Flexible control**: Choose the right mode for each situation
- **Better visibility**: Comprehensive monitoring and logging

### For Large Campaigns
- **Improved stability**: Dedicated process per campaign
- **Resource efficiency**: Background processing uses less UI resources
- **Parallel processing**: Multiple campaigns can run simultaneously
- **Progress persistence**: Resume monitoring after app restart

## Future Enhancements

Planned improvements:
- **Scheduled campaigns**: Set future start times
- **Campaign templates**: Reusable campaign configurations
- **Advanced monitoring**: Performance metrics and analytics
- **Batch operations**: Bulk campaign management
- **Integration APIs**: External system integration
