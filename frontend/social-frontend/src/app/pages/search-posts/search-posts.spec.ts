import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { SearchPosts } from './search-posts';
import { Post } from '../../models/post';
import { DescriptionEventsService } from '../../services/description-events';

function makePost(id: number): Post {
  return {
    id,
    image_filename: 'example.jpg',
    image_status: 'READY',
    image_description: null,
    description_status: 'NONE',
    content: 'hello',
    username: 'alice',
    created_at: '2024-01-01T00:00:00Z',
    sentiment_status: 'NONE',
    sentiment_label: null,
    sentiment_score: null,
  } as Post;
}

describe('SearchPosts', () => {
  let component: SearchPosts;
  let fixture: ComponentFixture<SearchPosts>;
  let httpMock: HttpTestingController;

  const mockDescriptionEvents: Partial<DescriptionEventsService> = {
    subscribeToPost: () =>
      of({
        description_status: 'READY',
        image_description: 'test description',
      } as any),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchPosts, HttpClientTestingModule],
      providers: [
        { provide: DescriptionEventsService, useValue: mockDescriptionEvents },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SearchPosts);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('search() triggers GET /posts?user=...', () => {
    component.username = 'alice';
    component.search();

    const req = httpMock.expectOne((r) => {
      return (
        r.method === 'GET' &&
        r.url === 'http://localhost:8000/posts' &&
        r.params.get('user') === 'alice'
      );
    });

    req.flush([makePost(1)]);
    expect(component.posts.length).toBe(1);
    expect(component.posts[0].id).toBe(1);
  });

  it('onDescribeImage triggers POST /posts/:id/describe and sets PENDING optimistically', () => {
    component.posts = [makePost(1)];

    component.onDescribeImage(1);

    // optimistic
    expect(component.posts[0].description_status).toBe('PENDING');

    const req = httpMock.expectOne('http://localhost:8000/posts/1/describe');
    expect(req.request.method).toBe('POST');
    req.flush({ status: 'PENDING' });

    // mocked SSE emits READY
    expect(component.posts[0].description_status).toBe('READY');
    expect(component.posts[0].image_description).toBe('test description');
  });

  it('onAnalyzeSentiment triggers POST /posts/:id/sentiment', () => {
    component.posts = [makePost(1)];

    component.onAnalyzeSentiment(1);

    // optimistic
    expect(component.posts[0].sentiment_status).toBe('PENDING');

    const req = httpMock.expectOne('http://localhost:8000/posts/1/sentiment');
    expect(req.request.method).toBe('POST');
    req.flush({ status: 'PENDING' });

    // no GET expectation here anymore
  });
});
