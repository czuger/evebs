module Modules::Nvl

  # If a number does not exist : then assigns it to minus infinity
  def nvl( number )
    number ? number : -Float::INFINITY
  end

end