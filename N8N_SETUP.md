# n8n Workflow Automation Setup

This project now uses [n8n](https://github.com/n8n-io/n8n) for workflow automation instead of the custom AI chat system.

## What is n8n?

n8n is a fair-code workflow automation platform that gives technical teams the flexibility of code with the speed of no-code. With 400+ integrations, native AI capabilities, and a fair-code license, n8n lets you build powerful automations while maintaining full control over your data and deployments.

## Database Configuration

The n8n instance is configured to use the PostgreSQL database with the following credentials:

- **Host**: dpg-d32ft1idbo4c73adbolg-a.oregon-postgres.render.com
- **Port**: 5432
- **Database**: n8n_database_aumq
- **Username**: n8n_database_aumq_user
- **Password**: [Stored as environment variable]

## Deployment Files

- `render-n8n.yaml` - Render deployment configuration
- `package-n8n.json` - Node.js dependencies for n8n
- `n8n-env-template.txt` - Environment variables template

## Features Replaced by n8n

The following components from the original Flask app have been replaced by n8n workflows:

- ✅ AI chat functionality
- ✅ OpenRouter API integration
- ✅ Workflow automation
- ✅ Data processing pipelines
- ✅ Integration with external services

## What's Still Available

The following components remain in the Flask app:

- ✅ User authentication system
- ✅ Project management
- ✅ File management
- ✅ Database operations
- ✅ Static file serving

## Getting Started with n8n

1. Deploy using the `render-n8n.yaml` configuration
2. Access the n8n interface at your deployed URL
3. Create workflows to replace the AI chat functionality
4. Set up integrations with your preferred AI services
5. Configure webhooks and automation triggers

## Migration Notes

- The AI chat API endpoints have been removed
- OpenRouter integration is now handled through n8n workflows
- Database schema remains compatible
- User authentication system is preserved
