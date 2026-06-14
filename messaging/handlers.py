def process_created_handler(
    event
):

    print()

    print(
        "[EVENT]"
        " PROCESS CREATED"
    )

    print(event)


def process_completed_handler(
    event
):

    print()

    print(
        "[EVENT]"
        " PROCESS COMPLETED"
    )

    print(event)


def process_failed_handler(
    event
):

    print()

    print(
        "[EVENT]"
        " PROCESS FAILED"
    )

    print(event)