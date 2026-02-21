import React from 'react';

export default function FormBuilder({ fields, register, errors, onSubmit, submitLabel = 'حفظ' }) {
  return (
    <form onSubmit={onSubmit}>
      {fields.map((field) => (
        <div key={field.name} className="form-group">
          <label className="form-label">{field.label}</label>
          {field.type === 'select' ? (
            <select className="form-input" {...register(field.name)}>
              {field.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          ) : field.type === 'textarea' ? (
            <textarea className="form-input" rows={4} {...register(field.name)} />
          ) : (
            <input
              className="form-input"
              type={field.type || 'text'}
              placeholder={field.placeholder}
              {...register(field.name)}
            />
          )}
          {errors[field.name] && (
            <p className="form-error">{errors[field.name]?.message}</p>
          )}
        </div>
      ))}
      <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
        {submitLabel}
      </button>
    </form>
  );
}
