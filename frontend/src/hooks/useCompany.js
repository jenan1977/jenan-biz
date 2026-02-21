import { useSelector, useDispatch } from 'react-redux';
import { setCurrentCompany } from '../store/companySlice';

export function useCompany() {
  const dispatch = useDispatch();
  const { currentCompany, companies } = useSelector((state) => state.company);

  const selectCompany = (company) => dispatch(setCurrentCompany(company));

  return { currentCompany, companies, selectCompany };
}
