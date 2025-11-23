import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchPosts } from './search-posts';

describe('SearchPosts', () => {
  let component: SearchPosts;
  let fixture: ComponentFixture<SearchPosts>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchPosts]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SearchPosts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
