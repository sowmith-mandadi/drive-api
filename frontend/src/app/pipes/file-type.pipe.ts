import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'fileType'
})
export class FileTypePipe implements PipeTransform {
  transform(fileType: string): string {
    if (!fileType) return 'Unknown';
    
    // Handle MIME types
    if (fileType.includes('/')) {
      const type = fileType.split('/')[1].toUpperCase();
      
      // Special case handling
      if (type.includes('PDF')) return 'PDF';
      if (type.includes('PNG') || type.includes('JPEG') || type.includes('JPG') || type.includes('GIF')) return 'IMAGE';
      if (type.includes('ZIP') || type.includes('COMPRESSED')) return 'ZIP';
      if (type.includes('DOCUMENT')) return 'DOC';
      if (type.includes('SHEET')) return 'XLS';
      if (type.includes('PRESENTATION')) return 'PPT';
      
      return type;
    }
    
    // Already formatted
    return fileType.toUpperCase();
  }
}
