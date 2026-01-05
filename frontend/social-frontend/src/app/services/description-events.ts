import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface DescriptionEventPayload {
  post_id: number;
  description_status?: string;
  image_description?: string | null;
}

@Injectable({ providedIn: 'root' })
export class DescriptionEventsService {
  private apiUrl = 'http://localhost:8000';

  subscribeToPost(postId: number): Observable<DescriptionEventPayload> {
    return new Observable((observer) => {
      const es = new EventSource(`${this.apiUrl}/events/posts/${postId}`);

      es.addEventListener('description', (ev: MessageEvent) => {
        try {
          observer.next(JSON.parse(ev.data));
        } catch (e) {
          // ignore bad payload
        }
      });

      es.onerror = () => {
        // SSE auto-reconnects; do not complete on transient errors
      };

      return () => {
        es.close();
      };
    });
  }
}
