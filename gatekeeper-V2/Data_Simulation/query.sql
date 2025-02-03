case
    when count(*) > 0 then extract(
      hours
      from
        $__timeTo() - time
    ) || E '\n' || 'hrs' || E '\n' || extract(
      minutes
      from
        $__timeTo() - time
    ) || E '\n' || 'min'
    else extract(
      hour
      from
        age($__timeTo(), $__timeFrom())
    ) || E '\n' || 'hrs' || E '\n' || extract(
      minutes
      from
        age($__timeTo(), $__timeFrom())
    ) || E '\n' || 'min'
  end as dur