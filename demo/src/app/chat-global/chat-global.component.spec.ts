import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatGlobalComponent } from './chat-global.component';

describe('ChatGlobalComponent', () => {
  let component: ChatGlobalComponent;
  let fixture: ComponentFixture<ChatGlobalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatGlobalComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ChatGlobalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
