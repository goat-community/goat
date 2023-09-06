import { useDispatch } from "react-redux";
import type { AppDispatch } from "@/lib/store";
export const useAppDispatch = () => useDispatch<AppDispatch>();
