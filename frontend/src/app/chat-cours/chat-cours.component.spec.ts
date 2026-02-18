import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatCoursComponent } from './chat-cours.component';

describe('ChatCoursComponent', () => {
  let component: ChatCoursComponent;
  let fixture: ComponentFixture<ChatCoursComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatCoursComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ChatCoursComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
