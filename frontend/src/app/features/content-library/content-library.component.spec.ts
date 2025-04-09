import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContentLibraryComponent } from './content-library.component';

describe('ContentLibraryComponent', () => {
  let component: ContentLibraryComponent;
  let fixture: ComponentFixture<ContentLibraryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContentLibraryComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContentLibraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
