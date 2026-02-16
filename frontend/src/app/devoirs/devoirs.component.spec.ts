import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DevoirsComponent } from './devoirs.component';

describe('DevoirsComponent', () => {
  let component: DevoirsComponent;
  let fixture: ComponentFixture<DevoirsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DevoirsComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DevoirsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
