import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { AllPosts } from './all-posts';
import { Post } from '../../models/post';

/**
 * Stub for app-post-card so we don't depend on its template or logic.
 * We only care about the generateDescription output.
 */
@Component({
  selector: 'app-post-card',
  standalone: true,
  template: '',
})
class PostCardStub {
  @Input({ required: true }) post!: Post;
  @Output() generateDescription = new EventEmitter<number>();
}

describe('AllPosts', () => {
  let component: AllPosts;
  let fixture: ComponentFixture<AllPosts>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    })
      .overrideComponent(AllPosts, {
        set: {
          imports: [PostCardStub],
        },
      })
      .compileComponents();

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

  it('emitting generateDescription triggers POST /posts/:id/describe', () => {
    component.ngOnInit();

    const basePost: any = {
      id: 1,
      image_filename: 'test.png',
      image_status: 'READY',
      content: null,
      username: 'alice',
      created_at: new Date().toISOString(),
      image_description: null,
      description_status: 'NONE',
    };

    // 1) flush first GET /posts
    const getReq1 = httpMock.expectOne('http://localhost:8000/posts');
    expect(getReq1.request.method).toBe('GET');
    getReq1.flush([basePost]);

    fixture.detectChanges();

    // 2) emit output from stub post card
    const stubDe = fixture.debugElement.children.find(
      (de) => de.componentInstance instanceof PostCardStub
    );
    expect(stubDe).toBeTruthy();

    const stub = stubDe!.componentInstance as PostCardStub;
    stub.generateDescription.emit(1);

    // 3) expect POST /posts/1/describe
    const postReq = httpMock.expectOne('http://localhost:8000/posts/1/describe');
    expect(postReq.request.method).toBe('POST');
    postReq.flush({ status: 'PENDING' });

    // 4) if component polls GET /posts/1, flush one READY response
    const pollReqs = httpMock.match('http://localhost:8000/posts/1');
    if (pollReqs.length > 0) {
      pollReqs.forEach((r) =>
        r.flush({
          ...basePost,
          description_status: 'READY',
          image_description: 'A short description.',
        })
      );
    }

    // 5) IMPORTANT: flush any additional GET /posts the component might trigger (refresh)
    const extraGets = httpMock.match('http://localhost:8000/posts');
    extraGets.forEach((r) => r.flush([basePost]));

    fixture.detectChanges();
  });
});
