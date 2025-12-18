import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PostCard } from './post-card';
import { Post } from '../../models/post';

function makePost(status: 'PENDING' | 'READY' | 'FAILED'): Post {
  return {
    id: 1,
    image_filename: 'example.jpg',
    image_status: status,
    content: 'hello',
    username: 'alice',
    created_at: '2024-01-01T00:00:00Z',
  };
}

describe('PostCard integration', () => {
  let fixture: ComponentFixture<PostCard>;
  let component: PostCard;
  let element: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PostCard],
    }).compileComponents();

    fixture = TestBed.createComponent(PostCard);
    component = fixture.componentInstance;
    element = fixture.nativeElement as HTMLElement;
  });

  it('uses reduced image when status is READY', async () => {
    component.post = makePost('READY');
    component.ngOnChanges();      // simulate @Input change
    fixture.detectChanges();
    await fixture.whenStable();

    const img = element.querySelector('img.post-thumb') as HTMLImageElement | null;
    expect(img).not.toBeNull();
    expect(img!.getAttribute('src')).toBe(
      'http://localhost:8000/static/reduced/example.jpg',
    );

    // no processing message in READY state
    const processing = element.querySelector('.img-processing');
    expect(processing).toBeNull();
  });

  it('uses original image and shows pending message when status is PENDING', async () => {
    component.post = makePost('PENDING');
    component.ngOnChanges();
    fixture.detectChanges();
    await fixture.whenStable();

    const img = element.querySelector('img.post-thumb') as HTMLImageElement | null;
    expect(img).not.toBeNull();
    expect(img!.getAttribute('src')).toBe(
      'http://localhost:8000/static/original/example.jpg',
    );

    const processing = element.querySelector('.img-processing') as HTMLElement | null;
    expect(processing).not.toBeNull();
    expect(processing!.textContent).toContain('Preview is being generated');
  });

  it('uses original image and shows failed message when status is FAILED', async () => {
    component.post = makePost('FAILED');
    component.ngOnChanges();
    fixture.detectChanges();
    await fixture.whenStable();

    const img = element.querySelector('img.post-thumb') as HTMLImageElement | null;
    expect(img).not.toBeNull();
    expect(img!.getAttribute('src')).toBe(
      'http://localhost:8000/static/original/example.jpg',
    );

    const processing = element.querySelector('.img-processing') as HTMLElement | null;
    expect(processing).not.toBeNull();
    expect(processing!.textContent).toContain(
      'Preview generation failed (showing original).',
    );
  });
});
