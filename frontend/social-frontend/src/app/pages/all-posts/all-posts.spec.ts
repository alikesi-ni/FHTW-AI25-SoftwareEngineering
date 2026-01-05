import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { AllPosts } from './all-posts';
import { Post } from '../../models/post';

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
  };
}

describe('AllPosts', () => {
  let fixture: ComponentFixture<AllPosts>;
  let component: AllPosts;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AllPosts, HttpClientTestingModule],
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

  it('onDescribeImage triggers POST /posts/:id/describe', () => {
    // Arrange: init + flush initial load
    fixture.detectChanges();
    httpMock.expectOne('http://localhost:8000/posts').flush([makePost(1)]);

    // Act: call the handler directly (unit-test parent logic)
    component.onDescribeImage(1);

    // Assert: request is made
    const req = httpMock.expectOne('http://localhost:8000/posts/1/describe');
    expect(req.request.method).toBe('POST');
    req.flush({ status: 'PENDING' });

    // We don't assert SSE here; that's DescriptionEventsService's job.
    // But we *can* assert optimistic UI:
    const p = component.posts.find(x => x.id === 1)!;
    expect(p.description_status).toBe('PENDING');
  });

  it('onAnalyzeSentiment triggers POST /posts/:id/sentiment', () => {
    fixture.detectChanges();
    httpMock.expectOne('http://localhost:8000/posts').flush([makePost(1)]);

    component.onAnalyzeSentiment(1);

    const req = httpMock.expectOne('http://localhost:8000/posts/1/sentiment');
    expect(req.request.method).toBe('POST');
    req.flush({}); // backend returns something; not important here

    // pollSentiment will call GET /posts/1 at least once
    const pollReq = httpMock.expectOne('http://localhost:8000/posts/1');
    expect(pollReq.request.method).toBe('GET');
    pollReq.flush({
      ...makePost(1),
      sentiment_status: 'READY',
      sentiment_label: 'POSITIVE',
      sentiment_score: 0.95,
    });

    const p = component.posts.find(x => x.id === 1)!;
    expect(p.sentiment_status).toBe('READY');
    expect(p.sentiment_label).toBe('POSITIVE');
  });
});
