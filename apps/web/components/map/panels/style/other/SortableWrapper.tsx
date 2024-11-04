import type { DragEndEvent } from "@dnd-kit/core";
import { DndContext, closestCenter } from "@dnd-kit/core";
import { restrictToVerticalAxis } from "@dnd-kit/modifiers";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";

const SortableWrapper = ({
  items,
  children,
  handleDragEnd,
}: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  items: any[];
  children: React.ReactNode;
  handleDragEnd: (event: DragEndEvent) => void;
}) => (
  <DndContext
    collisionDetection={closestCenter}
    modifiers={[restrictToVerticalAxis]}
    onDragEnd={handleDragEnd}
    autoScroll={false}>
    <SortableContext items={items} strategy={verticalListSortingStrategy}>
      {children}
    </SortableContext>
  </DndContext>
);

export default SortableWrapper;
