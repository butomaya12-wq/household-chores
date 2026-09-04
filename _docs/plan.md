# Household Chores — MVP Plan

## Goal

Help family members organize household chores by defining what needs to be done, assigning responsibility, setting a deadline, and tracking completion.

## Users

Members of one household.

## MVP Features

1. Create a household chore.
2. Assign one family member as the responsible person.
3. Set a required due date and an optional due time.
4. Mark an assigned chore as completed.

## Acceptance Criteria

### 1. Create a chore

- A user can create a chore with a title.
- The title cannot be empty.
- After saving, the chore appears in the household chore list.

### 2. Assign a responsible person

- An existing chore can be assigned to one family member.
- The assigned person is visible on the chore.
- Only one responsible person can be assigned in the MVP.

### 3. Set a due date

- Every chore must have a due date.
- A due time may optionally be added.
- The due date is visible after saving.
- A chore cannot be saved without a due date.
- A due date in the past is not accepted.

### 4. Mark a chore as completed

- The assigned person can mark the chore as completed.
- The chore status changes from Open to Completed.
- Other household members can see that the chore is completed.
- Completed chores are no longer shown as active chores.

## Out of Scope

- Push notifications.
- Family budget and payments.
- Medical calendar.
- Meal planning.
- Multiple responsible people for one chore.
- Organizer approval of completed chores.
- Automatic duplicate detection.
- Recurring chores.

## Constraints

- One chore has one responsible person in the MVP.
- Every chore must have a due date.
- Only the assigned person can mark their chore as completed.


