module Esi::Errors
  class NotFound < Base

    def pause
      sleep 60
    end

    # Not found should never retry. Upper level of the application should handle it.
    # In case of daily history download there are a lot of non existing items (given by ESI but non existing)
    def retry?
      false
    end

  end
end
