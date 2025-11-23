import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListPosts } from './list-posts';

describe('ListPosts', () => {
  let component: ListPosts;
  let fixture: ComponentFixture<ListPosts>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListPosts]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListPosts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
