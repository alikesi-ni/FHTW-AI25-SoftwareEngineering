import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { AllPosts } from './all-posts';
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

describe('AllPosts', () => {
  let fixture: ComponentFixture<AllPosts>;
  let component: AllPosts;
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
      imports: [AllPosts, HttpClientTestingModule],
      providers: [
        { provide: DescriptionEventsService, useValue: mockDescriptionEvents },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AllPosts);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('loads posts on init (GET /posts)', () => {
    fixture.detectChanges(); // triggers ngOnInit -> loadPosts()

    const req = httpMock.expectOne('http://localhost:8000/posts');
    expect(req.request.method).toBe('GET');
    req.flush([makePost(1)]);

    expect(component.posts.length).toBe(1);
    expect(component.posts[0].id).toBe(1);
  });

  it('onDescribeImage triggers POST /posts/:id/describe and sets PENDING optimistically', () => {
    fixture.detectChanges();
    httpMock.expectOne('http://localhost:8000/posts').flush([makePost(1)]);

    component.onDescribeImage(1);

    // optimistic update
    const p0 = component.posts.find((x) => x.id === 1)!;
    expect(p0.description_status).toBe('PENDING');

    const req = httpMock.expectOne('http://localhost:8000/posts/1/describe');
    expect(req.request.method).toBe('POST');
    req.flush({ status: 'PENDING' });

    // since we mock SSE to emit READY, component should update when subscription fires
    const p1 = component.posts.find((x) => x.id === 1)!;
    expect(p1.description_status).toBe('READY');
    expect(p1.image_description).toBe('test description');
  });

  it('onAnalyzeSentiment triggers POST /posts/:id/sentiment', () => {
    fixture.detectChanges();
    httpMock.expectOne('http://localhost:8000/posts').flush([makePost(1)]);

    component.onAnalyzeSentiment(1);

    // optimistic update (your component likely sets PENDING)
    const p = component.posts.find((x) => x.id === 1)!;
    expect(p.sentiment_status).toBe('PENDING');

    const req = httpMock.expectOne('http://localhost:8000/posts/1/sentiment');
    expect(req.request.method).toBe('POST');
    req.flush({ status: 'PENDING' });

    // IMPORTANT: we do NOT expect a GET /posts/1 here anymore
    // because sentiment is async and may be updated via refresh/polling elsewhere.
  });
});
