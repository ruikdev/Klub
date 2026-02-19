import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-ocr',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './ocr.component.html',
  styleUrl: './ocr.component.css'
})
export class OcrComponent {
  selectedFiles: File[] = [];
  isDragging = false;
  loading = false;
  error: string | null = null;
  result: any = null;

  constructor(private apiService: ApiService) {}

  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) this.addFiles(Array.from(input.files));
    input.value = '';
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
    if (event.dataTransfer?.files) {
      this.addFiles(Array.from(event.dataTransfer.files));
    }
  }

  addFiles(files: File[]): void {
    const images = files.filter(f => f.type.startsWith('image/'));
    this.selectedFiles = [...this.selectedFiles, ...images];
    this.error = null;
    this.result = null;
  }

  removeFile(index: number): void {
    this.selectedFiles = this.selectedFiles.filter((_, i) => i !== index);
  }

  upload(): void {
    if (!this.selectedFiles.length) return;
    this.loading = true;
    this.error = null;
    this.apiService.sendOcrImages(this.selectedFiles).subscribe({
      next: (data) => {
        this.result = data;
        this.loading = false;
        this.selectedFiles = [];
      },
      error: (err) => {
        this.error = err?.error?.error ?? 'Une erreur est survenue.';
        this.loading = false;
      }
    });
  }

  reset(): void {
    this.result = null;
    this.error = null;
    this.selectedFiles = [];
  }
}
