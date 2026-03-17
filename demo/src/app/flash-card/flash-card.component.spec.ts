import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FlashCardComponent } from './flash-card.component';

describe('FlashCardComponent', () => {
  let component: FlashCardComponent;
  let fixture: ComponentFixture<FlashCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FlashCardComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(FlashCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
