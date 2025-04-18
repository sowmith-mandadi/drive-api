# Google Cloud Next '25 Content Management System

This project provides a content management system for Google Cloud Next '25 event content, including sessions, speakers, presentations, and other materials.

## Features

- **Modern Google Cloud Next Design**: Sleek, professional UI matching Google Cloud Next branding
- **Content Management**: Create, edit, and organize event content
- **Speaker Management**: Track speakers, their bios, and session assignments
- **AI Integration**: AI-powered content tagging and summarization
- **Advanced Search**: Find and filter content with powerful search capabilities

## Key Components

1. **Home Dashboard**: Overview of event content metrics and quick actions
2. **Content Form**: Create and edit sessions, speakers, and other content types
3. **Conference Schema Management**: Define content types and fields
4. **Content Review Workflow**: Approve and manage content review process

## Theme

The UI is themed after Google Cloud Next '25 event, using:

- **Color Scheme**: Google Cloud blue (#1a73e8) and green (#34a853)
- **Typography**: Google Sans font
- **Card-based interface**: Modern, clean card layouts
- **Material Design**: Angular Material components with custom styling

## Getting Started

1. **Install dependencies**:
   ```
   npm install
   ```

2. **Run development server**:
   ```
   npm run start
   ```

3. **Access the application**:
   Navigate to `http://localhost:4200/`

## Project Structure

- `src/app/features/content-management`: Content management components
- `src/app/features/home`: Dashboard components
- `src/app/shared`: Shared components, pipes, and directives
- `src/app/core`: Core services, guards, and interceptors

## UI/UX Features

- Responsive design for all device sizes
- Smooth animations and transitions
- Intuitive navigation and workflows
- Google Cloud Next visual identity

## Technologies

- Angular 16+
- Angular Material
- RxJS
- SCSS with custom theming
- Google Cloud integration

## Cloud Shell Deployment

To deploy this Angular application in a cloud shell environment:

1. Create a deployment zip file:
   ```bash
   chmod +x create-deploy-zip.sh
   ./create-deploy-zip.sh
   ```

2. Upload the generated `frontend-deploy.zip` to your cloud shell.

3. In cloud shell, unzip the file:
   ```bash
   unzip frontend-deploy.zip
   cd temp_deploy
   ```

4. Run the setup script:
   ```bash
   ./cloud-shell-setup.sh
   ```

5. Start the application:
   ```bash
   npm start
   ```

If you need to connect to a backend API, edit the `cloud-shell-setup.sh` script to uncomment and modify the line that updates the backend API URL in `proxy.conf.json`.

### Node.js Version

This project uses Angular 19, which requires Node.js 20.x or higher. If you encounter Node.js version issues in cloud shell:

```bash
# Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.nvm/nvm.sh

# Install and use Node.js 20
nvm install 20
nvm use 20
```
