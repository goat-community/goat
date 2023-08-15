import type { NonPostableEvtLike, NonPostableEvt, UnpackEvt } from "evt";
import { Evt } from "evt";
import { useEvt } from "evt/hooks";
// Copyright (c) 2020 GitHub user u/garronej
import { useGuaranteedMemo } from "powerhooks/useGuaranteedMemo";

export function useNonPostableEvtLike<E extends NonPostableEvtLike<unknown> | undefined>(
  evtLike: E
): NonPostableEvt<UnpackEvt<E>> {
  const evt = useGuaranteedMemo(() => Evt.create<any>(), [evtLike]);

  useEvt(
    (ctx) => {
      if (evtLike === undefined) {
        return;
      }
      evtLike.attach(ctx, (data) => evt.post(data));
    },
    [evtLike]
  );

  return (evtLike === undefined ? undefined : evt) as any;
}
