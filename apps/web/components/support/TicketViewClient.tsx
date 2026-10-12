"use client";

import dynamic from "next/dynamic";

// The reply composer reads its draft from localStorage while rendering, so it must not be server-rendered
// (hydration mismatch); browser-only also gives the phone layout from the first frame (see useSupportMobile).
const TicketView = dynamic(() => import("@/components/support/TicketView"), { ssr: false });

const TicketViewClient = ({ ticketRef }: { ticketRef: string }) => <TicketView ticketRef={ticketRef} />;

export default TicketViewClient;
